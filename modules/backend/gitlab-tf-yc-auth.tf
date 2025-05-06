 # Create a service account for accessing Yandex Cloud via Terraform through GitLab
resource "yandex_iam_service_account" "gitlab_tf" {
  name = "${var.project_prefix}--gitlab-terraform-sa"
}

# This gives full administrative access to manage resources within the folder.
resource "yandex_resourcemanager_folder_iam_member" "sa-admin" {
  folder_id = data.yandex_client_config.client.folder_id
  role      = "admin"
  member    = "serviceAccount:${yandex_iam_service_account.gitlab_tf.id}"
}

# Create an authorized access key for the sa
# This key will be used for Terraform authentication and API calls.
resource "yandex_iam_service_account_key" "this" {
  service_account_id = "${yandex_iam_service_account.gitlab_tf.id}"
  key_algorithm      = "RSA_2048" # RSA_4096

}

# This file will be used in Terraform for authentication when applying the configuration.
resource "local_file" "gitlab_tf_key" {
  filename    = "../secrets/backend/.key.json"
  content     = <<EOH
  {
    "id": "${yandex_iam_service_account_key.this.id}",
    "service_account_id": "${yandex_iam_service_account.gitlab_tf.id}",
    "created_at": "${yandex_iam_service_account_key.this.created_at}",
    "key_algorithm": "${yandex_iam_service_account_key.this.key_algorithm}",
    "public_key": ${jsonencode(yandex_iam_service_account_key.this.public_key)},
    "private_key": ${jsonencode(yandex_iam_service_account_key.this.private_key)}
  }
  EOH
}