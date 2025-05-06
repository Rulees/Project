output "backend_tf" {
  description = "Provides the Terraform backend configuration for storing state in Yandex S3 and DynamoDB. Includes necessary settings and endpoints for S3 and DynamoDB integration."
  value       = module.backend.backend_tf 
  }
