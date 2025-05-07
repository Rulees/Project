#!/bin/bash
VALUE="" # or ""

find . -type f -name terragrunt.hcl -execdir bash -c "
    set -o pipefail
    path=\$(pwd)

    if output=\$(terragrunt output -json 2>/dev/null); then
        # Extract matching entries (key-value pairs)
        entries=\$(echo \"\$output\" | jq --arg key \"$VALUE\" -r '
            to_entries[]
            | select(.key | test(\$key; \"i\"))
            | [.key, (if (.value.value | type == \"array\") 
                      then (.value.value | map(tostring) | join(\", \")) 
                      else (.value.value | tostring) end)]
            | @tsv
        ')

        if [[ -n \"\$entries\" ]]; then
            printf \"\\n[OUTPUT FROM: %s]\\n\" \"\$path\"
            
            # Determine max key length
            max=\$(echo \"\$entries\" | cut -f1 | awk '{ print length }' | sort -nr | head -n1)

            # Print aligned output
            echo \"\$entries\" | while IFS=\$'\\t' read -r key val; do
                printf \"%-*s: %s\\n\" \"\$max\" \"\$key\" \"\$val\"
            done
        fi
    fi
" \;