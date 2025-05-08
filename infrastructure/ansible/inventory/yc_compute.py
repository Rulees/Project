#!/usr/bin/env python3

from __future__ import (absolute_import, division, print_function)

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.utils.display import Display
from itertools import permutations
import yandexcloud
import os
import sys
import json
import yaml
from google.protobuf.json_format import MessageToDict
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub
from yandex.cloud.compute.v1.instance_service_pb2 import ListInstancesRequest
from yandex.cloud.resourcemanager.v1.cloud_service_pb2 import ListCloudsRequest
from yandex.cloud.resourcemanager.v1.cloud_service_pb2_grpc import CloudServiceStub
from yandex.cloud.resourcemanager.v1.folder_service_pb2 import ListFoldersRequest
from yandex.cloud.resourcemanager.v1.folder_service_pb2_grpc import FolderServiceStub

display = Display()

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'yc_compute'

    def verify_file(self, path):
        return True

    def __init__(self):
        """Инициализация конфигурации"""
        super(InventoryModule, self).__init__()
        self.inventory = {}
        self.args = sys.argv
        self.list = '--list' in self.args
        self.host = '--host' in self.args

    def _load_config(self, path):
        """Загружаем конфигурацию из YAML файла."""
        try:
            with open(path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise AnsibleError(f"Не удалось загрузить конфигурацию из {path}: {str(e)}")

    def _init_client(self, config):
        """Инициализация клиента Yandex Cloud SDK с токеном."""
        
        work_dir = os.environ.get("WORK_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
        
        token = os.getenv("OAUTH_TOKEN", None)
        if not token:
            token = config.get('oauth_token', None)

        if token:
            sdk = yandexcloud.SDK(token=token)
            self.using_sa = False
            display.v("✅ Используется OAuth авторизация.")
        else:
            sa_key_path = os.path.join(work_dir, "secrets/shared/yc_compute_viewer_sa_key.json")
            try:
                with open(sa_key_path, 'r') as f:
                    sa_key = json.load(f)
                sdk = yandexcloud.SDK(service_account_key=sa_key)
                self.using_sa = True
                display.v(f"✅ Используется SA авторизация из {sa_key_path}")
            except Exception as e:
                raise AnsibleError(f"Ошибка загрузки SA ключа из {sa_key_path}: {str(e)}")
        self.instance_service = sdk.client(InstanceServiceStub)
        self.folder_service = sdk.client(FolderServiceStub)
        self.cloud_service = sdk.client(CloudServiceStub)

    def _get_clouds(self, config):
        """Получаем облака из Yandex Cloud."""
        all_clouds = MessageToDict(self.cloud_service.List(ListCloudsRequest()))["clouds"]

        # Проверка совпадения облаков в конфиге и облаке
        missing_clouds = [cloud for cloud in config.get('yc_clouds', []) if cloud not in [c['name'] for c in all_clouds]]
        if missing_clouds:
            display.warning(f"Облака в конфиге, которых нет в Yandex Cloud: {missing_clouds}")

        # Фильтруем облака, если в конфиге указаны yc_clouds
        return [cloud for cloud in all_clouds if cloud['name'] in config.get('yc_clouds', [])]

    def _get_folders(self, cloud_id, config):
        """Получаем папки из облака Yandex Cloud."""
        all_folders = MessageToDict(self.folder_service.List(ListFoldersRequest(cloud_id=cloud_id)))["folders"]

        # Проверка совпадения папок в конфиге и облаке
        missing_folders = [folder for folder in config.get('yc_folders', []) if folder not in [f['name'] for f in all_folders]]
        if missing_folders:
            display.warning(f"Папки в конфиге, которых нет в Yandex Cloud: {missing_folders}")
        
        # Фильтруем папки, если в конфиге указаны yc_folders
        return [folder for folder in all_folders if folder['name'] in config.get('yc_folders', [])]

    def _get_all_hosts(self, config):
        """Получаем все хосты из папок в Yandex Cloud."""
        hosts = []

        if getattr(self, 'using_sa', False) and config.get('yc_folder_id'):
            # SA mode: use yc_folder_id directly
            for folder_id in config.get('yc_folder_id', []):
                try:
                    instances = self.instance_service.List(ListInstancesRequest(folder_id=folder_id))
                    dict_ = MessageToDict(instances)
                    if dict_:
                        hosts += dict_.get("instances", [])
                    else:
                        display.warning(f"Нет инстансов в папке {folder_id}")
                except Exception as e:
                    display.warning(f"Ошибка при получении инстансов из папки {folder_id}: {str(e)}")
        else:
            # OAuth mode: discover clouds/folders dynamically
            for cloud in self._get_clouds(config):
                for folder in self._get_folders(cloud["id"], config):
                    instances = self.instance_service.List(ListInstancesRequest(folder_id=folder["id"]))
                    dict_ = MessageToDict(instances)
                    if dict_:
                        hosts += dict_.get("instances", [])
                    else:
                        display.warning(f"Нет инстансов в папке {folder['name']}")

        return hosts


    def _process_hosts(self, hosts, config):
        """Processes hosts and creates a valid Ansible inventory structure"""

        inventory = {
            "_meta": {
                "hostvars": {}
            },
            "all": {
                "hosts": [],
                "children": ["yandex_dynamic"]
            },
            "yandex_dynamic": {
                "hosts": []
            }
        }

        for host in hosts:
            # Process only running instances
            if host["status"] != "RUNNING":
                continue

            # Get the IP address for the instance
            ip = self._get_ip_for_instance(host)
            if ip:
                host["ansible_host"] = ip  
            
            # Сохраняем переменные для каждого хоста в _meta
            inventory["_meta"]["hostvars"][host["name"]] = {
                "ansible_host": host["ansible_host"],
            }

            # Добавляем хост в список всех хостов в "all"
            inventory["all"]["hosts"].append(host["name"])

            # Добавляем хост в группу "yandex_dynamic"
            inventory["yandex_dynamic"]["hosts"].append(host["name"])

            # Process dynamic groups from labels
            if "labels" in host:
                label_groups = []

                for label_key, label_value in host["labels"].items():
                    if label_value:
                        key_value = f"{label_key}_{label_value}".replace("-", "_")
                        label_groups.append(key_value)

                        if key_value not in inventory["all"]["children"]:
                            inventory["all"]["children"].append(key_value)

                        if key_value not in inventory:
                            inventory[key_value] = {"hosts": []}
                        inventory[key_value]["hosts"].append(host["name"])

                    # Create group based only on label_key
                    key_value = label_key
                    if key_value not in inventory["all"]["children"]:
                        inventory["all"]["children"].append(key_value)
                    if key_value not in inventory:
                        inventory[key_value] = {"hosts": []}
                    inventory[key_value]["hosts"].append(host["name"])

                # Determine combination depth: use all if not specified
                label_count = len(label_groups)
                configured_max = config.get("group_combination_depth")
                max_depth = configured_max if configured_max is not None else label_count

                # Generate all permutations from 2 up to max_depth
                for r in range(2, min(max_depth, label_count) + 1):
                    for combo in permutations(label_groups, r):
                        combo_group = "__".join(combo)
                        if combo_group not in inventory["all"]["children"]:
                            inventory["all"]["children"].append(combo_group)
                        if combo_group not in inventory:
                            inventory[combo_group] = {"hosts": []}
                        inventory[combo_group]["hosts"].append(host["name"])


        return inventory

    def parse(self, inventory, loader, path, cache=True):
        """Парсим аргументы и обрабатываем инвентарь."""
        super(InventoryModule, self).parse(inventory, loader, path, cache=cache)
        
        # Получаем текущую рабочую директорию (откуда был запущен Ansible)
        current_dir = os.getcwd()
        path = os.path.join(current_dir, "yc_compute.yml")  # Join the directory with the config file path
        if not os.path.isfile(path):
            # try /inventory/yc_compute.yml
            path = os.path.join(current_dir, 'inventory', "yc_compute.yml")
        if not os.path.isfile(path):
            raise AnsibleError(f"Файл конфигурации {path} не найден!")

        # Чтение конфигурации
        config = self._load_config(path)
        
        # Инициализация клиента
        self._init_client(config)

        # Получение хостов
        hosts = self._get_all_hosts(config)

        # Обработка хостов
        inventory_data = self._process_hosts(hosts, config)

        # Output as JSON instead of YAML
        if self.list:
            print(json.dumps(inventory_data, indent=4))
        else:
            print("No arguments passed. Expected --list")


    def _get_ip_for_instance(self, instance):
        """Get the IP address for the instance."""
        interfaces = instance["networkInterfaces"]
        for interface in interfaces:
            address = interface["primaryV4Address"]
            if address:
                if address.get("oneToOneNat"):
                    return address["oneToOneNat"]["address"]
                else:
                    return address["address"]
        return None


if __name__ == "__main__":
    inventory = InventoryModule()
    inventory.parse(None, None, None)
