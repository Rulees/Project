#!/usr/bin/env python3
import subprocess
import sys

def run_destroy(env):
    path = f"infrastructure/{env}"
    print(f"💥 Destroying infrastructure in {path}")
    subprocess.run(["terragrunt", "run-all", "destroy", "--terragrunt-non-interactive"], cwd=path, check=True)

if __name__ == "__main__":
    env = sys.argv[1]
    run_destroy(env)
