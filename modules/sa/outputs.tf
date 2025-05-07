output "sa_id" {
  description = "Service account id"
    value       = var.create_mode ? yandex_iam_service_account.this[0].id : data.yandex_iam_service_account.existing[0].id
}

output "sa_name" {
  description = "The final name of the created service account"
  value       = local.sa_name
}

output "key_path" {
  description = "The file system path where the SA key was saved."
  value       = var.create_mode ? local_file.key_json[0].filename : var.key_path
}