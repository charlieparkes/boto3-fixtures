-include $(shell [ -e .build-harness ] || curl -sSL -o .build-harness "https://git.io/mintel-build-harness"; echo .build-harness)

.PHONY: init
init: bh/init
	@$(MAKE) bh/venv pipenv

.PHONY: docs
docs: pipenv
	$(WITH_PIPENV) $(MAKE) -C docs clean html

.PHONY: test
test: dummy_lambda/dist/build.zip pytest


dummy_lambda/dist/.venv:
	$(WITH_PIPENV) pip install -r <(PIPENV_QUIET=1 pipenv --bare lock -r) --ignore-installed --target $@

.PHONY: build-test-lambda
build-test-lambda: python/distif
	@make dummy_lambda/dist/.venv
	pip install dist/boto3-fixtures-*.tar.gz --target=dummy_lambda/dist/.venv --upgrade --no-deps --ignore-requires-python
	@cd dummy_lambda; make build

dummy_lambda/dist/build.zip:
	$(MAKE) build-test-lambda

.PHONY: release_patch
release_patch: bumpversion/release_patch

.PHONY: release_minor
release_minor: bumpversion/release_minor

.PHONY: release_major
release_major: bumpversion/release_major

.PHONY: clean
clean: python/clean/dist pipenv/clean python/clean
	@cd dummy_lambda; make clean
	@$(MAKE) bh/clean
