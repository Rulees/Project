locals {
  expanded_security_group_runners = flatten([
    for rule in var.security_group_runners : [
      for port in rule.ports : [
        for cidr in rule.v4_cidr_blocks : {
          direction   = rule.direction
          description = rule.description
          protocol    = rule.protocol
          from_port   = port
          to_port     = port
          cidr_block  = cidr
        }
      ]
    ]
  ])
}


resource "yandex_vpc_security_group" "this" {
  name        = "${var.project_prefix}--sg--${var.env}"
  description = "Combined security group for (web and internal) + (ingress and egress)"
  network_id  = var.network_id  # In the end we get vpc_id from module network

  dynamic "ingress" {
    for_each = [for rule in local.expanded_security_group_runners : rule if rule.direction == "ingress"]
    content {
      description    = ingress.value.description
      protocol       = ingress.value.protocol
      from_port      = ingress.value.from_port
      to_port        = ingress.value.to_port
      v4_cidr_blocks = [ingress.value.cidr_block]  # Оборачиваем в список
    }
  }

  dynamic "egress" {
    for_each = [for rule in local.expanded_security_group_runners : rule if rule.direction == "egress"]
    content {
      description    = egress.value.description
      protocol       = egress.value.protocol
      from_port      = egress.value.from_port
      to_port        = egress.value.to_port
      v4_cidr_blocks = [egress.value.cidr_block]
    }
  }
}
