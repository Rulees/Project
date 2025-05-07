locals {
  ec2_name         = "${var.project_prefix}--${var.ec2_name}-${random_id.this.hex}--${var.env}"
  # static_ip        = var.static_ip ? {external_ipv4_address = {zone_id = var.static_ip_zone_id}} : null
  # metadata is used of broken mechanism of enable_oslogin and ssh-connection... 
  custom_metadata  = {user-data  = templatefile("cloud-init.yml", {
    username       = var.enable_oslogin_or_ssh_keys.ssh_user
    ssh_key        = var.enable_oslogin_or_ssh_keys.ssh_key
  })}
}


module "yc-ec2" {
  source = "github.com/terraform-yc-modules/terraform-yc-compute-instance?ref=1.0.1"

  # GENERAL
  description                   = "Virtual Machine"
  zone                          = var.zone
  allow_stopping_for_update     = var.allow_stopping_for_update
  scheduling_policy_preemptible = var.scheduling_policy_preemptible
  serial_port_enable            = var.serial_port_enable
  labels                        = var.labels
  custom_metadata               = local.custom_metadata


  # COMPUTE RESOURCES
  name                          = local.ec2_name
  platform_id                   = var.platform_id 
  cores                         = var.cores
  core_fraction                 = var.core_fraction
  memory                        = var.memory
  gpus                          = var.gpus
  boot_disk                     = var.boot_disk

  # NETWORK
  network_interfaces            = var.network_interfaces
  
  # SSH
  enable_oslogin_or_ssh_keys    = var.enable_oslogin_or_ssh_keys
}

resource "random_id" "this" {
  byte_length = 2
}

# STATIC-IP-WITH-DDOS-PROTECTION
resource "yandex_vpc_address" "addr" {
  count = var.static_ip_ddos_protection ? 1 : 0

  external_ipv4_address {
    zone_id                  = "ru-central1-a"
    ddos_protection_provider = "qrator"
  }
}
