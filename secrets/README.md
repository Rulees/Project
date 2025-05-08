# ADMIN: bootstrap secrets (S3 backend, full SA, root SSH)          >>> only for full control / owner
# OPS  : operational secrets (CI/CD, Ansible, viewer SA, certs)     >>> for pipelines and limited human access
# DEV  : env-specific secrets for development services              >>> scoped to dev usage only
# PROD : env-specific secrets for production services               >>> strictly for production runtime
