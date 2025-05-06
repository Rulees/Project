# Configure Terragrunt to automatically store tfstate files in an S3 bucket
generate "backend" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
    
  terraform {
    backend "s3" {
      region         = "ru-central1"
      bucket         = "project-dildakot--yc-backend--k2bz6lv7"                                                          # change
      key            = "${path_relative_to_include()}/terraform.tfstate"

      dynamodb_table = "project-dildakot--yc-backend--state-lock-table"                                                  # change

      endpoints = {
        s3       = "https://storage.yandexcloud.net",
        dynamodb = "https://docapi.serverless.yandexcloud.net/ru-central1/b1gle99ifk9rj88rn6h0/etno47ncj5i827trgopu"      # change
      }

      skip_credentials_validation = true
      skip_region_validation      = true
      skip_requesting_account_id  = true
      skip_s3_checksum            = true
    }
  }
  EOF
}


# Generate an YC provider block
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF

  # PROVIDER.TF
  terraform {
    required_providers {
      yandex = {
        source  = "yandex-cloud/yandex"
        version = "= 0.127.0"
      }
      aws = {
        source  = "hashicorp/aws"
        version = "= 5.44.0"
      }
      random = {
        source = "hashicorp/random"
        version = "= 3.6.3"
      }
      time = {
        source = "hashicorp/time"
        version = "= 0.12.1"
      }
    }
    required_version = ">= 1.9.4"
  }

  provider "yandex" {
    folder_id = var.folder_id
    zone      = var.region
  }


  # VARIABLES
  variable "region" {
    description = "Example: ru-central1"
    type        = string
  }

  variable "folder_id" {
    description = "ID of folder"
    type        = string
  }
  EOF
}


locals {
  work_dir           = get_env("WORK_DIR")
  region             = "ru-central1"
  folder_id          = "b1ghomnle3pg309t5gu0"
  project_prefix     = "project"
  env_vars           = read_terragrunt_config(find_in_parent_folders("env.hcl"))
}


inputs = {
  work_dir          = local.work_dir
  region            = local.region
  folder_id         = local.folder_id
  project_prefix    = local.project_prefix
}
