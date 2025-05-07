# GENERAL
variable "project_prefix" {
  description = "A prefix used for naming resources related to the project."
  type        = string
}

# CONCRETE
variable "sa_name" {
  description = "Name of the service account"
  type        = string
}

variable "roles" {
  description = "IAM roles to bind to the service account"
  type        = list(string)
}

variable "key_path" {
  description = "Path to save SA JSON key (should match project secrets structure)"
  type        = string
}

variable "create_mode" {
  type        = bool
  default     = false
  description = "If true — create SA and key. If false — use existing SA via data lookup."
}
