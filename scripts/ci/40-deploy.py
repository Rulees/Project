#!/usr/bin/env python3

import asyncio, os, sys
from pathlib import Path
# Set up project root and discovery imports
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "ci"))
from discover_services import find_project_root, find_matching_services, build_group_name


async def run_playbook(m):
    group = build_group_name(m["env"], m["app"], m["service"])
    playbook = m["path"] / "playbook.yml"

    if not playbook.exists():
        print(f"⚠️ Skipping {group}: playbook not found at {playbook}")
        return

    print(f"\n🚀 [DEPLOY] {group} → {playbook}")

    cmd = [
        "ansible-playbook", str(playbook),
        "-i", str(ROOT / "infrastructure" / "ansible" / "inventory" / "yc_compute.py"),
        "-l", group, "-e", f"env={m['env']}", "-e", f"app={m['app']}", "-e", f"service={m['service']}",
        "--diff"
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(ROOT / "infrastructure" / "ansible"),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    stdout, _ = await proc.communicate()

    if proc.returncode != 0:
        print(f"❌ Ansible failed for {group}")
        print(stdout.decode())
    else:
        print(f"✅ Ansible succeeded for {group}")
        print(stdout.decode())

async def main():
    os.chdir(find_project_root())

    env = os.getenv("ENV")
    app = os.getenv("APP")
    service = os.getenv("SERVICE")

    matches = find_matching_services(env, app, service)
    if not matches:
        print("⚠️ No matching services for deploy.")
        return

    print("📦 Matched groups:")
    for m in matches:
        print(f" - {build_group_name(m['env'], m['app'], m['service'])}")

    # Run all deployments concurrently
    await asyncio.gather(*(run_playbook(m) for m in matches))

if __name__ == "__main__":
    asyncio.run(main())
