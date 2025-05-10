#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

# Set up project root and discovery imports
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from discover_services import find_project_root, find_matching_services, build_group_name

def main():
    os.chdir(find_project_root())

    env = os.getenv("ENV")
    app = os.getenv("APP")
    service = os.getenv("SERVICE")

    matches = find_matching_services(env, app, service)
    if not matches:
        print("⚠️ No matching services for deploy.")
        sys.exit(0)

    print("📦 Matched groups:")
    for m in matches:
        print(f" - {build_group_name(m['env'], m['app'], m['service'])}")

    for m in matches:
        group = build_group_name(m["env"], m["app"], m["service"])
        playbook = m["path"] / "playbook.yml"

        if not playbook.exists():
            print(f"⚠️ Skipping {group}: playbook not found at {playbook}")
            continue

        print(f"\n🚀 [DEPLOY] {group} → {playbook}")
        try:
            subprocess.run([
                "ansible-playbook", str(playbook),
                "-i", str(ROOT / "infrastructure" / "ansible" / "inventory" / "yc_compute.py"),
                "-l", group,
                "-e", f"env={m['env']}",
                "-e", f"app={m['app']}",
                "-e", f"service={m['service']}",
                "--diff"
            ],
            cwd=ROOT / "infrastructure" / "ansible",
            check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Ansible failed for {group}")
            print(e)
            continue

if __name__ == "__main__":
    main()
