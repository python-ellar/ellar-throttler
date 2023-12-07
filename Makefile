.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Removing cached python compiled files
	find . -name \*pyc  | xargs  rm -fv
	find . -name \*pyo | xargs  rm -fv
	find . -name \*~  | xargs  rm -fv
	find . -name __pycache__  | xargs  rm -rfv
	find . -name .ruff_cache  | xargs  rm -rfv

install: ## Install dependencies
	flit install --deps develop --symlink

install-full: ## Install dependencies
	make install
	pre-commit install -f

lint:fmt ## Run code linters
	ruff check ellar_throttler tests
	mypy ellar_throttler

fmt format:clean ## Run code formatters
	ruff format ellar_throttler tests
	ruff check --fix ellar_throttler tests

test: ## Run tests
	pytest tests

test-cov: ## Run tests with coverage
	pytest --cov=ellar_throttler --cov-report term-missing tests

pre-commit-lint: ## Runs Requires commands during pre-commit
	make clean
	make fmt
	make lint
