# VPC
output "vpc_id" {
  value       = data.yandex_vpc_network.vpc.id
  description = "Standard VPC id"
}

output "vpc_name" {
  value       = data.yandex_vpc_network.vpc.name
  description = "Standard VPC name"
}



# SUBNET
output "subnet_id" {
  value       = data.yandex_vpc_subnet.subnet.id
  description = "Subnet is selected by variable of zone"
}

output "subnet_name" {
  value       = data.yandex_vpc_subnet.subnet.name
  description = "Subnet is selected by variable of zone"
}

output "subnet_cidr" {
  value       = data.yandex_vpc_subnet.subnet.v4_cidr_blocks[0]
  description = "CIDR block of subnetwork"
}