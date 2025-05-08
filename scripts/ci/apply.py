#!/usr/bin/env python3
import subprocess
import sys
import json

def run_terragrunt(env, app, service):
    path = f"infrastructure/{env}/vpc/{app}/{service}"
    print(f"🔧 Applying terragrunt in {path}")
    subprocess.run(["terragrunt", "apply", "-auto-approve"], cwd=path, check=True)

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        with open(sys.argv[1]) as f:
            services = json.load(f)
        for svc in services:
            run_terragrunt(svc["env"], svc["app"], svc["service"])
    else:
        env, app, service = sys.argv[1], sys.argv[2], sys.argv[3]
        run_terragrunt(env, app, service)
