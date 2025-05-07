#!/bin/zsh

# GitLab API конфигурация
PROJECT_ID="" 
GITLAB_API_PROJECT_TOKEN="" # from /secrets/shared/gitlab.env
SOPS_ADMIN_KEY=$(cat ~/.sops/age_admin_key.txt)
SOPS_DEV_KEY=$(cat ~/.sops/age_dev_key.txt)
SOPS_PROD_KEY=$(cat ~/.sops/age_prod_key.txt)


GITLAB_API_URL="https://gitlab.com/api/v4"
HEADERS="PRIVATE-TOKEN: $GITLAB_API_PROJECT_TOKEN"

# Функция для добавления переменной в GitLab CI/CD
add_gitlab_variable() {

  curl --silent --request POST "$GITLAB_API_URL/projects/$PROJECT_ID/variables" \
       --header "$HEADERS"      \
       --form "key=$1"           \
       --form "variable_type=$2"  \
       --form "masked=$3"          \
       --form "protected=$4"        \
       --form "value=$5"             \
       --form "description=$6"        \
}

#                                                            [TYPE]     [MASKED]  [PROTECTED]             [VALUE]                          [DESCRIPTION]
add_gitlab_variable "SOPS_ADMIN_KEY"                        "env_var"     true       false            "$SOPS_ADMIN_KEY"               "SOPS AGE PRIVATE KEY FOR DECRYPTING ADMIN SECRETS"
add_gitlab_variable "SOPS_DEV_KEY"                          "env_var"     true       false            "$SOPS_DEV_KEY"                 "SOPS AGE PRIVATE KEY FOR DECRYPTING DEV/SHARED SECRETS"
add_gitlab_variable "SOPS_PROD_KEY"                         "env_var"     true       false            "$SOPS_PROD_KEY"                "SOPS AGE PRIVATE KEY FOR DECRYPTING PROD/SHARED SECRETS"



echo "\n\nСКРИПТ ЗАВЕРШЁН!"
# Send Variables
# cd /root/terraform/yc-tf-backend/scripts
# chmod +x add_variables_to_gitlab.sh && ./add_variables_to_gitlab.sh 
