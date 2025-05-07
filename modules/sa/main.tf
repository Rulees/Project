# Use the right SA ID (from resource or data)
locals {
  sa_id                = var.create_mode ? yandex_iam_service_account.this[0].id : data.yandex_iam_service_account.existing[0].id
  sa_name              = "${var.project_prefix}--${var.sa_name}"
}

# Create SA only if create_mode == true
resource "yandex_iam_service_account" "this" {
  count                = var.create_mode ? 1 : 0

  name                 = local.sa_name
  folder_id            = var.folder_id
  lifecycle {prevent_destroy = true}
}

# Looking for existing SA if create_mode == false
data "yandex_iam_service_account" "existing" {
  count                = var.create_mode ? 0 : 1

  name                 = local.sa_name
  folder_id            = var.folder_id
}


# IAM roles
resource "yandex_resourcemanager_folder_iam_member" "this" {
  for_each             = toset(var.roles)
  
  folder_id            = var.folder_id
  role                 = each.value
  member               = "serviceAccount:${local.sa_id}"
}

# Key
resource "yandex_iam_service_account_key" "this" {
  count                = var.create_mode ? 1 : 0

  service_account_id   = local.sa_id
  key_algorithm        = "RSA_2048"
  description          = "key for ${var.sa_name}"
  lifecycle {prevent_destroy = true}
}

resource "local_file" "key_json" {
  count                = var.create_mode ? 1 : 0    # Pipiline has to use encrypted version, and it's about create mode = false. So block "count" is really necessary

  filename             = var.key_path
  content              = <<EOH
{
  "id": "${yandex_iam_service_account_key.this[0].id}",
  "service_account_id": "${local.sa_id}",
  "created_at": "${yandex_iam_service_account_key.this[0].created_at}",
  "key_algorithm": "${yandex_iam_service_account_key.this[0].key_algorithm}",
  "public_key": ${jsonencode(yandex_iam_service_account_key.this[0].public_key)},
  "private_key": ${jsonencode(yandex_iam_service_account_key.this[0].private_key)}
}
EOH
  lifecycle {prevent_destroy = true}
}
