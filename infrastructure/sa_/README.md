# 🔐 Service Accounts: Manual Apply Only

Эти модули создают **сервисные аккаунты и ключи**, которые к сожалению один раз нужно создать вручную, удалить remote-state, а потом использовать блок "data"


1) Create SA + key + localfile
     "create_mode = true"
      terragrunt apply


2) Encrypt new-created-secret
     find secrets/ -type f -exec sops --encrypt --in-place {} \;


3) Remove SA-resources from state manually/script/pre-commit-hook 
     cd ./infrastructure/sa_/cert_downloader
     terragrunt state rm yandex_iam_service_account.this     || true
     terragrunt state rm yandex_iam_service_account_key.this || true
     terragrunt state rm local_file.key_json                 || true


4) Use existing SA via data
     "create_mode = false"
     git commit -v -m "commit" / terragrunt run-all apply/destroy(не удалит ключ и файл, отлично, потому что они вне состояния)


5) Rotate keys. Import SA-key, other will be recreated
     # FINDOUT SA_ID filter + Import sa via this filter
     yc iam service-account get --name project--cert-downloader | x yq repl 
     terragrunt import yandex_iam_service_account.this\[0\] "$(yc iam service-account get --name project--cert-downloader | yq .id)"


     "create_mode = true"
     terragrunt apply
     ...
     Step 2
     ....
     Step 3







1. Применить **один раз вручную**
2. Сразу **зашифровать через `sops`**
3. Только потом **коммитить в репозиторий**

---

## ❗ CI/CD НЕ создаёт эти ключи!

- Создание SA и ключей через CI — ЗАПРЕЩЕНО.
- CI только использует `.json`, зашифрованный в `secrets/`
- Для защиты sa-ключа-секрета от удаления испольузется prevent destroy на уровне модуля

---