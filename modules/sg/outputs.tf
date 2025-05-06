output "sg_id" {
  description = "Combined Security Group ID of {web access via VPN, internal access via SSH}"
  value       = yandex_vpc_security_group.this.id
}


output "sg_name" {
  description = "Combined Security Group ID of {web access via VPN, internal access via SSH}"
  value       = yandex_vpc_security_group.this.name
}