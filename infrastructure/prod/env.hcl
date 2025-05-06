locals {
  zone   = "ru-central1-a" # не поменял, хотя в старом проекте b
  env    = "prod"

# LABELS: env env_prod
  env_labels = {
    env  = "prod"
  }
}
