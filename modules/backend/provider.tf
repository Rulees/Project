terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "= 0.115.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.44.0"
    }
    random = {
      source = "hashicorp/random"
    }
    time = {
      source = "hashicorp/time"
    }
  }
  required_version = "= 1.9.4"
}

provider "yandex" {
  zone      = "ru-central1-a"
  folder_id = "b1ghomnle3pg309t5gu0"
}