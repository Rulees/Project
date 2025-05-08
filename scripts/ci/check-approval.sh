#!/bin/bash
set -e

echo "🔐 Проверка одобрений MR перед деплоем в прод..."

# === Задание переменных ===
# VARIABLES_FROM_GITLAB_PROJECT
APPROVERS_ARRAY=(${APPROVERS//,/ })
GITLAB_TOKEN="${GITLAB_API_BOT}"

# PREDEFINED_VARIABLES_OF_PIPELINE
API_URL="${CI_API_V4_URL}"
PROJECT_ID="${CI_PROJECT_ID}"
COMMIT_SHA="${CI_COMMIT_SHA}"
TARGET_BRANCH="${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}"

# === Получаем MR ===
MR_INFO=$(curl --silent --request GET \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "${API_URL}/projects/${PROJECT_ID}/merge_requests" \
  | jq -c ".[] | select(.sha == \"${COMMIT_SHA}\" and .state == \"opened\" and .target_branch == \"${TARGET_BRANCH}\")")

if [ -z "$MR_INFO" ]; then
  echo "❌ Merge Request не найден."
  exit 1
fi

MR_ID=$(echo $MR_INFO | jq '.iid')

# === Получаем approvals ===
APPROVALS=$(curl --silent --request GET \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "${API_URL}/projects/${PROJECT_ID}/merge_requests/${MR_ID}/approvals")

# Проверка на наличие одобрений от авторов
APPROVED=false
MAX_RETRIES=7  # Максимальное количество попыток
RETRY_DELAY=30  # Задержка между попытками в секундах

for ((i=1; i<=MAX_RETRIES; i++)); do
  # Список авторов, которые ещё не подтвердили
  NOT_APPROVED=()

  # Проверяем всех авторов
  for AUTHOR in "${APPROVERS_ARRAY[@]}"; do
    if ! echo "${APPROVALS}" | jq -e ".approved_by[] | select(.user.username == \"${AUTHOR}\")" > /dev/null; then
      NOT_APPROVED+=("${AUTHOR}")
    fi
  done

  # Если все одобрили, выходим
  if [ ${#NOT_APPROVED[@]} -eq 0 ]; then
    APPROVED=true
    break
  fi

  echo "⏳ Ожидаем одобрения от: ${NOT_APPROVED[*]} (попытка $i/${MAX_RETRIES})"
  sleep ${RETRY_DELAY}

  # Получаем обновлённые данные об одобрениях
  APPROVALS=$(curl --silent --request GET \
    --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "${API_URL}/projects/${PROJECT_ID}/merge_requests/${MR_ID}/approvals")
done

if [ "$APPROVED" = true ]; then
  echo "✅ MR одобрен всеми: ${APPROVERS[*]}"
else
  echo "❌ Не получено одобрение от всех: ${APPROVERS[*]}"
  exit 1
fi
