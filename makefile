ENV ?=
APP ?=
SERVICE ?=

.PHONY: create deploy destroy

create:
	python3 scripts/ci/20-create.py $(ENV) $(APP) $(SERVICE)

deploy:
	python3 scripts/ci/30-deploy.py $(ENV) $(APP) $(SERVICE)

destroy:
	python3 scripts/ci/40-destroy.py $(ENV) $(APP) $(SERVICE)