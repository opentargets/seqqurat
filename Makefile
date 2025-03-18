.PHONY: help

help:  ## Show the help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-9s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


### DEVELOPMENT TARGETS ###
.git/hooks/pre-commit:
	@ln -s $(shell pwd)/pre-commit.githook .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo pre-commit hook installed

.venv/bin/pytest:  # If we have pytest, it means we have installed dev dependencies
	@uv sync --all-extras --dev --quiet
	@echo dev dependencies installed

dev: .venv/bin/pytest .git/hooks/pre-commit  ## Install development dependencies and pre-commit hook

test: .venv/bin/pytest  ## Run the tests
	@uv run pytest

format: ## run formatting
	@echo "Running formatting tools..."
	@uv run --frozen ruff format src/$(APP_NAME) tests seqqurat.py

coverage: .venv/bin/pytest  ## Generate and show coverage reports
	@uv run coverage run -m pytest -qq && uv run coverage xml && uv run coverage report -m