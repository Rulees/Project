.PHONY: detect apply deploy destroy

detect:
	python3 scripts/ci/detect.py

apply:
	python3 scripts/ci/apply.py $(if $(filter %.json,$(firstword $(MAKECMDGOALS))),$(firstword $(MAKECMDGOALS)),$(ENV) $(APP) $(SERVICE))

deploy:
	python3 scripts/ci/deploy.py $(if $(filter %.json,$(firstword $(MAKECMDGOALS))),$(firstword $(MAKECMDGOALS)),$(ENV) $(APP) $(SERVICE))

destroy:
	python3 scripts/ci/destroy.py $(ENV)
