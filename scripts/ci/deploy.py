#!/usr/bin/env python3
import subprocess
import sys
import json

def run_ansible(env, app, service):
    group = f"env_{env}__app_{app}_{service}"
    playbook = f"infrastructure/ansible/playbooks/{service}.yml"
    print(f"🚀 Deploying Ansible to group {group} using playbook {playbook}")
    subprocess.run([
        "ansible-playbook",
        playbook,
        "-l", group,
        "-e", f"env={env}",
        "-e", f"app={app}",
        "-e", f"service={service}"
    ], check=True)

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        with open(sys.argv[1]) as f:
            services = json.load(f)
        for svc in services:
            run_ansible(svc["env"], svc["app"], svc["service"])
    else:
        env, app, service = sys.argv[1], sys.argv[2], sys.argv[3]
        run_ansible(env, app, service)
