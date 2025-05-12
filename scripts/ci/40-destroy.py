#!/usr/bin/env python3
import subprocess, os, sys
from pathlib import Path

# Корень проекта
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

# Импорт из твоего собственного discover_services.py
from discover_services import find_project_root, find_matching_services, build_group_name

def main():
    os.chdir(find_project_root())

    env = os.getenv("ENV")
    app = os.getenv("APP")
    service = os.getenv("SERVICE")

    if not env:
        print("❌ ENV is required (e.g. ENV=dev or ENV=prod)")
        sys.exit(1)

    # Working dir = путь до env
    working_dir = ROOT / "infrastructure" / env

    # include_dir строим по app и service
    if app and service:
        include_dir = f"vpc/{app}/{service}"
    elif app:
        include_dir = f"vpc/{app}"
    else:
        include_dir = None

    # Получаем сервисы по заданному фильтру
    matches = find_matching_services(env, app, service)
    
    if not matches:
        print("⚠️ No matching services found for destroy.")
        sys.exit(0)

    print("📦 Matched groups:")
    for m in matches:
        print(f" - {build_group_name(m['env'], m['app'], m['service'])}")

    # Формируем команду
    cmd = ["terragrunt", "destroy", "--all", "--non-interactive", "-lock=false", "-auto-approve"]
    if include_dir:
        cmd += ["--queue-include-dir", include_dir]
    cmd += ["--working-dir", str(working_dir)]

    print(f"\n💥 Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as err:
        print("❌ Terragrunt destroy failed.")
        print(err)
        sys.exit(err.returncode)

if __name__ == "__main__":
    main()
