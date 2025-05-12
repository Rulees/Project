## SOPS keys to decrypt /secrets/*
# 
ADMIN: bootstrap secrets (S3 backend, full SA, root SSH)          >>> only for full control / owner
OPS  : operational secrets (CI/CD, Ansible, viewer SA, certs)     >>> for pipelines and limited human access
DEV  : env-specific secrets for development services              >>> scoped to dev usage only
PROD : env-specific secrets for production services               >>> strictly for production runtime


# Description of  /secrets/ 

terragrunt(create.py)   /admin/remote-backend.env                  # AWS creds for accessing remote state
                        /admin/yc_admin_sa_key.json                # Admin service account for creating resources
                        /admin/yc_ssh_key                          # Private ssh-key for creating vm's with them



ansible(deploy.py)      /admin/yc_ssh_key                          # Private ssh-key for accessing vm's
                        /{dev,prod}/{app}/{service}/secret.env     # Specific {env}{app}{service}
                        /ops/yc_cert_downloader_sa_key.json        # YandexCloud Service account to get ssl-certficate for website
                        /ops/yc_compute_viewer_sa_key.json         # Ansible Dynamic inventory




approve(check-...sh)    APPROVERS_ARRAY                            # List of authors for approving merge requests(Manual)
                        APPROVERS_INFRA_ARRAY                      # List of authors for approving only specific folder /infrastructure(Manual)
                        GITLAB_API_PROJECT_TOKEN                   # BOT for approving merge requests and adding new comments to MR etc..
