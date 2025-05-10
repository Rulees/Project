ENV ?=
APP ?=
SERVICE ?=

.PHONY: detect create deploy destroy

detect:
	python3 scripts/ci/20-detect.py

create:
	yes | python3 scripts/ci/30-create.py $(ENV) $(APP) $(SERVICE)

deploy:
	python3 scripts/ci/40-deploy.py $(ENV) $(APP) $(SERVICE)

destroy:
	python3 scripts/ci/50-destroy.py $(ENV) $(APP) $(SERVICE)