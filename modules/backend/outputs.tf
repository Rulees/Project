output "backend_tf" {
  description = "Provides the Terraform backend configuration for storing state in Yandex S3 and DynamoDB. Includes necessary settings and endpoints for S3 and DynamoDB integration."
  value       = <<EOH

terraform {
  backend "s3" {
    region         = "ru-central1"
    bucket         = "${yandex_storage_bucket.backend.id}"
    key            = "backend/terraform.tfstate"

    dynamodb_table = "${aws_dynamodb_table.lock.id}"

    endpoints = {
      s3       = "https://storage.yandexcloud.net",
      dynamodb = "${yandex_ydb_database_serverless.lock.document_api_endpoint}"
    }

    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true
  }
}
EOH
}
