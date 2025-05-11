terraform {
  source = "${get_repo_root()}/modules//yc-ec2/"
}

include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

dependency "network" {
  config_path                             = "../../../network/"
  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan", "providers", "terragrunt-info", "show"]
  mock_outputs = {
    subnet_id = "subnet-id-fake"
  }
}

dependency "sg" {
  config_path                             = "../../../sg/"
  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan", "providers", "terragrunt-info", "show"]
  mock_outputs = {
    sg_id = "sg-id-fake"
  }
}

dependency "sa_cert_downloader" {
  config_path                             = "../../../../sa_/cert_downloader"
}

dependency "sa_compute_viewer" {
  config_path                             = "../../../../sa_/compute_viewer"
}


locals {
  env          = include.root.locals.env_vars.locals.env
  zone         = include.root.locals.env_vars.locals.zone
  work_dir     = include.root.locals.work_dir
  # labels
  env_labels     = include.root.locals.env_vars.locals.env_labels
  app_labels     = {app = "${basename(dirname(get_terragrunt_dir()))}"}
  service_labels = {service = "${basename(get_terragrunt_dir())}"}
  labels         = merge(local.env_labels, local.app_labels, local.service_labels)
}

inputs = {  
  # GENERAL
  env                           = local.env
  zone                          = local.zone
  allow_stopping_for_update     = true
  scheduling_policy_preemptible = true
  serial_port_enable            = false
  labels                        = local.labels

  

  # COMPUTE RESOURCES
  name                          = "vm"
  platform_id                   = "standard-v3"
  cores                         = 2
  core_fraction                 = 20
  memory                        = 4
  boot_disk = {
    type                        = "network-ssd"
    image_id                    = "fd8kc2n656prni2cimp5" # container-optimized-image
    size                        = 15
  }

  # NETWORK
  network_interfaces = [{
    subnet_id                   = dependency.network.outputs.subnet_id
    security_group_ids          = [dependency.sg.outputs.sg_id]
    
    # CHOICE (Uncomment one):   #1) Dynamic NAT  #2) Use static IP  #3) Enable DDoS-protected static IP
    nat                         = true
    # nat_ip_address              = "158.160.39.80"
  }]
  # static_ip_ddos_protection     = true

  # DNS(AUTO REDIRECT)
  dns = {
    zone_id                     = "dnsdejjcevumag5r1q11"
    name                        = "dev.arkselen.ru."
    ttl                         = 60
  }

  # SSH
  enable_oslogin_or_ssh_keys = {
    ssh_user                    = "melnikov"
    ssh_key                     = file("/root/.ssh/YC.pub")
  }
}
