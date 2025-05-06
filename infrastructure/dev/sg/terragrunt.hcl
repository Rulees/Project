# 2
terraform {
  source = "../../../modules//sg/"
}


include "root" {
  path = find_in_parent_folders("root.hcl")
  expose = true
}


dependency "network" {
  config_path                             = "../network/"
  mock_outputs_allowed_terraform_commands = ["init", "validate", "plan", "providers", "terragrunt-info", "show"] # Configure mock outputs for commands that are returned when there are no outputs available (e.g the module hasn't been applied yet.)
  mock_outputs = {
    vpc_id = "subnet-id-fake"
  }
}


inputs = {
  env        = include.root.locals.env_vars.locals.env
  zone       = include.root.locals.env_vars.locals.zone
  network_id = dependency.network.outputs.vpc_id
  

  security_group_runners = [
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
      v4_cidr_blocks = ["0.0.0.0/0"]
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
