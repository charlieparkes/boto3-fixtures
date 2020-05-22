-include $(shell [ -e .build-harness ] || curl -sSL -o .build-harness "https://git.io/mintel-build-harness"; echo .build-harness)

.PHONY: init
init: bh/init
	@$(MAKE) bh/venv pipenv

docs: pipenv
	$(WITH_PIPENV) $(MAKE) -C docs clean html
.PHONY: docs

dummy_lambda/dist/.venv:
	$(WITH_PIPENV) pip install -r <(PIPENV_QUIET=1 pipenv --bare lock -r) --ignore-installed --target $@

build-test-lambda: python/distif
	@make dummy_lambda/dist/.venv
	pip install dist/boto3_fixtures-*.tar.gz --target=dummy_lambda/dist/.venv --upgrade --no-deps --ignore-requires-python
	@cd dummy_lambda; make build
.PHONY: build-test-lambda

dummy_lambda/dist/build.zip:
	$(MAKE) build-test-lambda

release_patch: bumpversion/release_patch
.PHONY: release_patch

release_minor: bumpversion/release_minor
.PHONY: release_minor

release_major: bumpversion/release_major
.PHONY: release_major

.PHONY: clean
clean: python/clean/dist pipenv/clean python/clean
	@cd dummy_lambda; make clean
	@$(MAKE) bh/clean
