#!/bin/bash
# Install programms
set -e

echo "🔐 Проверка зашифрованных файлов в /secrets..."

if [[ -n "$CI_MERGE_REQUEST_IID" ]]; then
  echo "📦 MR detected — проверка через GitLab API"
FILES=$(curl --silent --header "PRIVATE-TOKEN: $GITLAB_API_PROJECT_TOKEN" \
  "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/changes" \
  | jq -r '.changes[].new_path' | grep '^secrets/' || true)
else
  echo "📦 Not an MR — проверка через git diff $CI_COMMIT_BEFORE_SHA..$CI_COMMIT_SHA"
  FILES=$(git diff --name-only "$CI_COMMIT_BEFORE_SHA" "$CI_COMMIT_SHA" | grep '^secrets/' || true)
fi

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
