terraform {
  source = "${get_repo_root()}/modules//sa"
}

include "root" {
  path = find_in_parent_folders("root.hcl")
  expose = true
}

locals {
  sa_name        = "cert-downloader"
}

inputs = {
  create_mode    = false # TRUE = create sa!  FALSE = use existing via data.*
  project_prefix = include.root.locals.project_prefix
  folder_id      = include.root.locals.folder_id
  sa_name        = local.sa_name
  roles          = ["certificate-manager.certificates.downloader"]
  key_path       = "${get_repo_root()}/secrets/ops/yc_${replace(local.sa_name, "-", "_")}_sa_key.json"
}