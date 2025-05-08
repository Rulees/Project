#!/usr/bin/env python3
import subprocess
import json

def detect_changed_paths():
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'origin/main...HEAD'],
        stdout=subprocess.PIPE,
        text=True
    )
    changed_files = result.stdout.strip().split('\n')

    services = set()
    for path in changed_files:
        parts = path.split('/')
        if len(parts) >= 5 and parts[0] == 'infrastructure':
            env = parts[1]
            app = parts[3]
            service = parts[4]
            group = f"env_{env}__app_{app}_{service}"
            services.add((env, app, service, group))

    output = [
        {'env': env, 'app': app, 'service': service, 'group': group}
        for (env, app, service, group) in sorted(services)
    ]

    with open('changed_services.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    detect_changed_paths()
