#!/bin/bash
set -e

echo "🔐 Проверка зашифрованных файлов в /secrets..."

FILES=$(git diff --name-only origin/main...HEAD | grep '^secrets/' || true)
has_errors=0

for file in $FILES; do
  [[ ! -f "$file" ]] && continue
  [[ "$file" == *.gitkeep ]] && continue
  [[ "$(basename "$file")" == "README.md" ]] && continue

  status_json=$(sops filestatus "$file" 2>/dev/null || echo '{"encrypted":false}')
  is_encrypted=$(echo "$status_json" | jq -r '.encrypted' 2>/dev/null)

  if [[ "$is_encrypted" != "true" ]]; then
    echo "❌ $file НЕ зашифрован (status: $status_json)"
    has_errors=1
  fi
done

if [[ "$has_errors" -ne 0 ]]; then
  echo "🛑 Найдены НЕзашифрованные секреты!"
  exit 1
fi

echo "✅ Все секреты зашифрованы корректно."
