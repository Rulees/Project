variable "project_prefix" {
  description        = "Name prefix of project."
  type               = string
}

variable "network_id" {
  description        = "Network(vpc) id"
  type               = string
}

variable "env" {
  description        = "Set 'prod' for production, or 'dev' for development"
  type               = string
}


variable "security_group_runners" {
  type = list(object({
    direction        = string  # "ingress" или "egress"
    description      = string
    protocol         = string
    ports            = list(number)
    v4_cidr_blocks   = list(string)
  }))
  default = [
    # Входящие правила
    {
      direction      = "ingress"
      description    = "Allow HTTP and HTTPS"
      protocol       = "TCP"
      ports          = [80, 443]
      v4_cidr_blocks = ["0.0.0.0/0"]
    },
    {
      direction      = "ingress"
      description    = "Allow SSH"
      protocol       = "TCP"
      ports          = [22]
      v4_cidr_blocks = ["192.168.0.0/24", "0.0.0.0/0"]
    },
    # Исходящие правила
    {
      direction      = "egress"
      description    = "Allow all outbound HTTP/HTTPS traffic"
      protocol       = "TCP"
      ports          = [80, 443]
      v4_cidr_blocks = ["0.0.0.0/0"]
    },
    {
      direction      = "egress"
      description    = "Allow all outbound SSH"
      protocol       = "TCP"
      ports          = [22]
      v4_cidr_blocks = ["0.0.0.0/0"]
    }
  ]
}

