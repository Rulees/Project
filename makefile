ENV ?=
APP ?=
SERVICE ?=

.PHONY: check_secrets decrypt_secrets create deploy check_approval destroy

check_secrets:
	bash scripts/ci/10-check-secrets.sh

decrypt_secrets:
	bash scripts/ci/decrypt_secrets.sh

create:
	python3 scripts/ci/20-create.py $(ENV) $(APP) $(SERVICE)

deploy:
	python3 scripts/ci/30-deploy.py $(ENV) $(APP) $(SERVICE)

check_approval:
	bash scripts/ci/40-check-approval.sh

destroy:
	python3 scripts/ci/50-destroy.py $(ENV) $(APP) $(SERVICE)

