#!/usr/bin/env python3
import subprocess, os, sys
from pathlib import Path

# 🔧 Add the project root and scripts/ci/ to sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from discover_services import find_project_root, find_matching_services, build_group_name

def main():
    os.chdir(find_project_root())
    env, app, service = os.getenv("ENV"), os.getenv("APP"), os.getenv("SERVICE")
    matches = find_matching_services(env, app, service)

    if not matches:
        print("⚠️ No matching services for deploy.")
        sys.exit(1)

    groups = [build_group_name(m["env"], m["app"], m["service"]) for m in matches if m["has_ansible"]]
    if not groups:
        print("⚠️ No matching services with Ansible playbooks.")
        sys.exit(1)

    print("📦 Matched groups:")
    for g in groups:
        print(f" - {g}")

    for m in matches:
        if not m["has_ansible"]:
            continue
        group = build_group_name(m["env"], m["app"], m["service"])
        playbook = m["path"] / "playbook.yml"
        print(f"\n🚀 [DEPLOY] {group} → {playbook}")
        try:
            subprocess.run([
                "ansible-playbook", str(playbook),
                "-l", group,
                "-e", f"env={m['env']}",
                "-e", f"app={m['app']}",
                "-e", f"service={m['service']}"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Ansible failed for {group}")
            print(e)
            continue

if __name__ == "__main__":
    main()
