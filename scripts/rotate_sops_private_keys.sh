#!/bin/bash
# 1) Decrypt secrets with current private keys
# 2) Get age public keys from .sops.yaml
# 3) Remove and Generate only keys inside ~/.sops, that contain public keys from .sops.yaml
# 4) Copy public key from new-created keys + Insert to .sops.yaml instad of old-ones 
# 5) Encrypt with new keys
#!/bin/bash


# set -euo pipefail

PROJECT_DIR="${HOME}/project"
SECRETS_DIR="${PROJECT_DIR}/secrets"
SOPS_CONFIG="${PROJECT_DIR}/.sops.yaml"
SOPS_KEYS_DIR="${HOME}/.sops"
SOPS_KEYS_FILE="${SOPS_KEYS_DIR}/age_keys.txt"

mkdir -p "$SOPS_KEYS_DIR"

cd "$PROJECT_DIR"

# Дешифруем все секреты
echo "🔓 Дешифруем секреты..."
find "$SECRETS_DIR" -type f -exec sops --decrypt --in-place {} \;

# Получаем старые публичные ключи
echo "📥 Извлекаем старые публичные ключи из .sops.yaml..."
mapfile -t OLD_KEYS < <(yq '.creation_rules[].key_groups[].age[]' "$SOPS_CONFIG")

# 3. Regenerate keys for each public key
echo "🔐 Regenerating keys in-place..."
NEW_KEYS=()
for PUB_KEY in "${OLD_KEYS[@]}"; do
  MATCHING_FILES=($(grep -rl "# public key: $PUB_KEY" "$SOPS_KEYS_DIR" || true))
  
  if [[ ${#MATCHING_FILES[@]} -eq 0 ]]; then
    echo "⚠️ No key file found for public key $PUB_KEY. Skipping."
    continue
  elif [[ ${#MATCHING_FILES[@]} -gt 1 ]]; then
    echo "❌ Multiple key files found for public key $PUB_KEY:"
    printf '   %s\n' "${MATCHING_FILES[@]}"
    echo "❌ Aborting to avoid ambiguity."
    exit 1
  fi

  FILE="${MATCHING_FILES[0]}"
  rm -f "$FILE"
  age-keygen -o "$FILE"
  PUB=$(grep '# public key:' "$FILE" | awk '{print $4}')
  NEW_KEYS+=("$PUB")
done

# 4. Replace .sops.yaml with new keys
echo "🔄 Replacing .sops.yaml keys with new public keys..."
for i in "${!NEW_KEYS[@]}"; do
  yq ".creation_rules[$i].key_groups[0].age = [\"${NEW_KEYS[$i]}\"]" -i "$SOPS_CONFIG"
done

# Обновляем age_keys.txt
echo "📝 Обновляем $SOPS_KEYS_FILE..."
TMP_KEYS="$(mktemp)"
find "$SOPS_KEYS_DIR" -name '*.txt' -exec grep '^AGE-SECRET-KEY-' {} \; > "$TMP_KEYS"
mv "$TMP_KEYS" "$SOPS_KEYS_FILE"

# Добавляем переменную окружения
PROFILE="${HOME}/.bashrc"
[[ -n "${ZSH_VERSION-}" ]] && PROFILE="${HOME}/.zshrc"
if ! grep -q 'export SOPS_AGE_KEY_FILE=' "$PROFILE"; then
  echo "export SOPS_AGE_KEY_FILE=\"$SOPS_KEYS_FILE\"" >> "$PROFILE"
  echo "📌 Добавлено в $PROFILE"
fi
export SOPS_AGE_KEY_FILE="$SOPS_KEYS_FILE"

# Перешифровываем все
echo "🔒 Перешифровываем секреты..."
find "$SECRETS_DIR" -type f -exec sops --encrypt --in-place {} \;

echo "✅ Готово: ключи обновлены и секреты перешифрованы!"
