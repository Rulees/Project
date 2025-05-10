#!/usr/bin/env python3
import subprocess, os, sys
from pathlib import Path

# 🔧 Add the project root and scripts/ci/ to sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from discover_services import find_project_root, find_matching_services, build_group_name

def main():
    os.chdir(find_project_root())

    env = os.getenv("ENV")
    app = os.getenv("APP")
    service = os.getenv("SERVICE")

    # ENV is required
    if not env:
        print("❌ ENV is required (e.g. ENV=dev or ENV=prod)")
        sys.exit(1)

    # Determine working directory and include dir
    working_dir = ROOT / "infrastructure" / env

    if app and service:
        include_dir = f"vpc/{app}/{service}"
    elif app:
        include_dir = f"vpc/{app}"
    else:
        include_dir = None

    # Find target services
    matches = find_matching_services(env, app, service)

    if not matches:
        print("⚠️ No matching services found for apply.")
        sys.exit(0)

    print("📦 Matched groups:")
    for m in matches:
        print(f" - {build_group_name(m['env'], m['app'], m['service'])}")

    # Build command
    cmd = ["terragrunt", "apply", "--all"]
    if include_dir:
        cmd += ["--terragrunt-include-dir", include_dir]
    cmd += ["--working-dir", str(working_dir)]

    print(f"\n🚀 Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as err:
        print("💥 Terragrunt apply failed.")
        print(err)
        sys.exit(err.returncode)

if __name__ == "__main__":
    main()
