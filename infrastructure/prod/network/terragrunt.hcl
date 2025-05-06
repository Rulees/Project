# 1
terraform {
  source = "../../../modules//network/"
}


include "root" {
  path = find_in_parent_folders("root.hcl")
  expose = true
}


inputs = {
  env  = include.root.locals.env_vars.locals.env
  zone = include.root.locals.env_vars.locals.zone
}
