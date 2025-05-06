# NETWORK
output "internal_ip" {
  description = "The internal IP address of the instance."
  value       = module.yc-ec2.internal_ip
}

output "external_ip" {
  description = "The external IP address of the instance."
  value       = module.yc-ec2.external_ip
}


# INSTANCE
output "instance_id" {
  description = "The ID of the instance."
  value       = module.yc-ec2.instance_id
}