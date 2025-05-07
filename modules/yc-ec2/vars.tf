# GENERAL
variable "project_prefix" {
  description = "Prefix used for naming resources (e.g., project name)"
  type        = string
}

variable "env" {
  description = "Environment for the instance (e.g., dev, prod)"
  type        = string
}

variable "zone" {
  description = "The availability zone where the virtual machine will be created. If it is not provided, the default provider folder is used."
  type        = string
}

variable "ec2_name" {
  description = "The short name of the instance. Example: linux-vm. Typically generated dynamically using project_prefix, env"
  type        = string
  default     = "vm"
}

variable "platform_id" {
  description = "The type of virtual machine to create."
  type        = string
  default     = "standard-v3"
}

variable "cores" {
  description = "Number of CPU cores."
  type        = number
  default     = 2
}

variable "core_fraction" {
  description = "Guaranteed CPU-Share during all the work.(50%, *%) If share is less than 100, vm provides the specified level of performance with a probability of a temporary increase up to 100%"
  type        = number
  default     = 20
}

variable "memory" {
  description = "Memory size(GB)."
  type        = number
  default     = 4
}

variable "gpus" {
  description = "Number of GPUs."
  type        = number
  default     = 0
}

variable "boot_disk" {
  description = "Configuration for the boot disk."
  type = object({
    type      = optional(string, "network-ssd")
    image_id  = optional(string, "fd8hp9las7k42nhld0pe")
    size      = optional(number, 15)
  })
}

variable "allow_stopping_for_update" {
  description = "Allow/Restrics stopping for update"
  type        = bool
  default     = true
}

variable "scheduling_policy_preemptible" {
  description = "Specifies type of vm as preemptible. That means cost is lower, but vm can be stopped accidentally without warning and won't be enabled"
  type        = bool
  default     = false
}

variable "serial_port_enable" {
  description = "Open/Close serial port for accessing-debugging vm in GUI"
  type        = bool
  default     = false
}

variable "labels" {
  description = "Instance labels. For example: default = {env = dev}"
  type        = map(string)
  default     = null
}

variable "custom_metadata" {
  description = "Add custom metadata to node-groups"
  type        = map(any)
  default     = {}
}

# NETWORK
variable "network_interfaces" {
  description = "List of network interfaces. Overrides 'subnet_id' and 'security_group_ids' if provided."
  type = list(object({
    subnet_id          = string
    security_group_ids = list(string)
    nat                = optional(bool, "true")
    nat_ip_address     = optional(string)
    dns_record         = optional(list(object({
      fqdn             = string
      dns_zone_id      = optional(string)
      ttl              = optional(number)
    })), [])
  }))
}

# DNS
variable "dns" {
  description = "DNS record configuration to redirect arkselen.ru to dynamic-server-ip without creating additional DNS-A-note in GUI for redirecting"
  type = object({
    zone_id   = string
    name      = string
    type      = optional(string, "A")
    ttl       = optional(number, 60)
  })
  default = null
}

# SSH
variable "enable_oslogin_or_ssh_keys" {
  description      = "Configuration for enabling OS Login or SSH keys for the instance."
  type = object({
    enable-oslogin = optional(string, "false") # it brokes my metadata if enabled
    ssh_user       = optional(string, null)
    ssh_key        = optional(string, null)    # public key content
  })
}

# STATIC-IP-WITH-DDOS-PROTECTION
variable "static_ip_ddos_protection" {
  description = "Enable/Disable using static ip"
  type        = bool
  default     = false
}