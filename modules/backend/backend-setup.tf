provider "aws" {
  region                      = "eu-west-1"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  access_key                  = yandex_iam_service_account_static_access_key.this.access_key
  secret_key                  = yandex_iam_service_account_static_access_key.this.secret_key
  endpoints {
    dynamodb = yandex_ydb_database_serverless.lock.document_api_endpoint
  }
}


data "yandex_client_config" "client" {}


locals {
  prefix = "${var.project_prefix}--${var.backend_prefix}"

  service_account_name = "${local.prefix}--sa"
  bucket_name          = "${local.prefix}--${random_string.unique_id.result}"
  kms_key_name         = "${local.prefix}--kms"
  ydb_database_name    = "${local.prefix}--ydb"
  dynamodb_table_name  = "${local.prefix}--state-lock-table"
}


# Create service account with structured name
resource "yandex_iam_service_account" "backend" {
  name = local.service_account_name
}


# Назначение роли сервисному аккаунту - storage
resource "yandex_resourcemanager_folder_iam_member" "sa-admin-s3" {
  folder_id   = data.yandex_client_config.client.folder_id
  role        = "storage.admin"
  member      = "serviceAccount:${yandex_iam_service_account.backend.id}"
}


# Назначение роли сервисному аккаунту - kms
resource "yandex_resourcemanager_folder_iam_member" "sa-editor-kms" {
  folder_id   = data.yandex_client_config.client.folder_id
  role        = "kms.editor"
  member      = "serviceAccount:${yandex_iam_service_account.backend.id}"
}


# Назначение роли сервисному аккаунту - ydb
resource "yandex_resourcemanager_folder_iam_member" "sa-editor-ydb" {
  folder_id   = data.yandex_client_config.client.folder_id
  role        = "ydb.editor"
  member      = "serviceAccount:${yandex_iam_service_account.backend.id}"
}


# Создание статического ключа доступа
resource "yandex_iam_service_account_static_access_key" "this" {
  service_account_id = yandex_iam_service_account.backend.id
}


# Создание симметричного ключа шифрования
resource "yandex_kms_symmetric_key" "this" {
  name            = local.kms_key_name
  rotation_period = "8760h" # 1год
}


# Создание бакета
resource "yandex_storage_bucket" "backend" {
  bucket     = local.bucket_name
  access_key = yandex_iam_service_account_static_access_key.this.access_key
  secret_key = yandex_iam_service_account_static_access_key.this.secret_key
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = yandex_kms_symmetric_key.this.id
        sse_algorithm     = "aws:kms"
      }
    }
  }
  versioning {
    enabled = true
  }
  lifecycle_rule {
    enabled = true
    noncurrent_version_expiration {
      days = 30
    }
  }
}


# Создание YDB-базы для блокировки state-файла
resource "yandex_ydb_database_serverless" "lock" {
  name = local.ydb_database_name
  location_id  = "ru-central1"
}


# Ожидание после создания YDB
resource "time_sleep" "wait_for_database" {
  create_duration = "120s"
  depends_on      = [yandex_ydb_database_serverless.lock]
}


# Создание таблицы в YDB для блокировки state-файла
resource "aws_dynamodb_table" "lock" {
  name         = local.dynamodb_table_name
  hash_key     = "LockID"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "LockID"
    type = "S"
  }
  depends_on   = [time_sleep.wait_for_database, yandex_resourcemanager_folder_iam_member.sa-editor-ydb, yandex_iam_service_account_static_access_key.this]
}


# Создание файла .env с ключами доступа
resource "local_file" "env" {
  content     = <<EOH
AWS_ACCESS_KEY_ID="${yandex_iam_service_account_static_access_key.this.access_key}"
AWS_SECRET_ACCESS_KEY="${yandex_iam_service_account_static_access_key.this.secret_key}"
EOH
  filename = "../../secrets/backend/.env"
}


resource "random_string" "unique_id" {
  length  = 8
  upper   = false
  lower   = true
  numeric = true
  special = false
}