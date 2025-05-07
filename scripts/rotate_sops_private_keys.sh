#!/bin/bash
# 1) Decrypt secrets with current private keys
# 2) Get age public keys from .sops.yaml
# 3) Remove and Generate only keys inside ~/.sops, that contain public keys from .sops.yaml
# 4) Copy public key from new-created keys + Insert to .sops.yaml instad of old-ones 
# 5) Encrypt with new keys



#!/bin/bash
set -euo pipefail

cd ~/project

# 1) Decrypt secrets
find secrets/ -type f -exec sops --decrypt --in-place {} \;

# 2) Extract public keys from .sops.yaml
mapfile -t OLD_KEYS < <(yq '.creation_rules[].key_groups[].age[]' .sops.yaml)

# 3) Match and delete old key files
KEY_FILES=()
for PUB_KEY in "${OLD_KEYS[@]}"; do
  FILE=$(grep -rl "# public key: $PUB_KEY" ~/.sops || true)
  [[ -n "$FILE" ]] && KEY_FILES+=("$FILE")
done

for FILE in "${KEY_FILES[@]}"; do
  rm -f "$FILE"
done

# 4) Regenerate keys
NEW_KEYS=()
for FILE in "${KEY_FILES[@]}"; do
  sops age-keygen --output "$FILE"
  PUB=$(grep '# public key:' "$FILE" | awk '{print $4}')
  NEW_KEYS+=("$PUB")
done

# 5) Rebuild ~/.sops/age_keys.txt
> ~/.sops/age_keys.txt
for FILE in "${KEY_FILES[@]}"; do
  grep '^AGE-SECRET-KEY-' "$FILE" >> ~/.sops/age_keys.txt
done

# 6) Export path to keys and add to ~/.zshrc if not present
export SOPS_AGE_KEY_FILE="$HOME/.sops/age_keys.txt"
grep -qxF 'export SOPS_AGE_KEY_FILE="$HOME/.sops/age_keys.txt"' ~/.zshrc || echo 'export SOPS_AGE_KEY_FILE="$HOME/.sops/age_keys.txt"' >> ~/.zshrc

# 7) Update .sops.yaml in-place
for i in "${!NEW_KEYS[@]}"; do
  yq eval ".creation_rules[$i].key_groups[0].age = [\"${NEW_KEYS[$i]}\"]" -i .sops.yaml
done

# 8) Re-encrypt
find secrets/ -type f -exec sops --encrypt --in-place {} \;

echo "✅ Keys rotated, secrets re-encrypted, config complete."
