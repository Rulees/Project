variable "backend_prefix" {
  description = "Prefix for backend resources: bucket, state-lock-table, sa... Must be globally unique. Example: yc-tf-backend"
  type        = string
}

variable "project_prefix" {
  description = "A prefix used for naming resources related to the project (e.g., 'dev', 'prod', or a custom name)."
  type        = string
}