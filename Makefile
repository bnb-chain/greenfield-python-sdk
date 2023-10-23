.PHONY: build
build: #Run buf to generate the proto files.
build:
	cd proto ; poetry run buf generate -vvv

.PHONY: install
install: #Install the package with poetry.
install:
	poetry install --with dev

.PHONY: test-unit
test-unit: #Test the package with poetry.
test-unit:
	poetry run pytest tests -m "not e2e" --asyncio-mode=auto

.PHONY: test-e2e
test-e2e: #Test the package with poetry.
test-e2e:
	poetry run pytest tests -m "not unit and not requires_config and not go_library and not localnet" --asyncio-mode=auto

.PHONY: test-e2e-complete
test-e2e-complete: #Test the package with poetry.
test-e2e-complete:
	poetry run pytest tests -m "not unit and not localnet and not go_library" --asyncio-mode=auto

.PHONY: test-e2e-extra-go
test-e2e-extra-go: #Test the package with poetry.
test-e2e-extra-go:
	poetry run pytest tests -m "not unit and not localnet" --asyncio-mode=auto


.PHONY: test-e2e-local
test-e2e-local: #Test the package with poetry.
test-e2e-local:
	echo "Check that you have a running Greenfield node locally"
	poetry run pytest tests -m "localnet and not requires_validator_account and not requires_storage_provider" --asyncio-mode=auto

.PHONY: black
black: #Run black.
black:
	poetry run black --check --line-length 120 greenfield_python_sdk tests

.PHONY: flake8
flake8: #Run flake8.
flake8:
	poetry run flake8 --config setup.cfg greenfield_python_sdk tests

.PHONY: isort
isort: #Run isort.
isort:
	poetry run isort --line-length 120 --diff --check-only --quiet .

.PHONY: mypy
mypy: #Run mypy.
mypy:
	poetry run mypy -p greenfield_python_sdk

.PHONY: lint
lint: #Run lint with black, flake8, isort and mypy
lint: black flake8 isort mypy

.PHONY: reformat
reformat: #Fix code with black and isort
reformat:
	poetry run isort --line-length 120 --quiet .
	poetry run black --line-length 120 greenfield_python_sdk tests
