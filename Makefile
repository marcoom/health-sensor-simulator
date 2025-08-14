SOURCE_DIR = ./health_sensor_simulator

.DEFAULT_GOAL := help
.ONESHELL:

.PHONY: setup-venv install install-dev run test test-coverage docs \
		docs-html docs-pdf docs-clean docker-build docker-run docker-remove \
		help clean dist

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
VENV ?= .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

SRC := src
SPHINXOPTS    ?=
SPHINXBUILD   ?= $(VENV)/bin/sphinx-build
DOCSSOURCEDIR = docs/source
DOCSBUILDDIR  = docs/build

# ------------------------------------------------------------
# ENVIRONMENT SETUP
# ------------------------------------------------------------

setup-venv:
	sudo add-apt-repository ppa:deadsnakes/ppa -y
	sudo apt update
	sudo apt install -y python3.11 python3.11-venv python3.11-dev
	python3.11 -m ensurepip --upgrade
	python3.11 -m venv $(VENV)

install:
	$(PIP) install -r requirements/base.txt

install-dev: install
	$(PIP) install -r requirements/dev.txt
	$(PIP) install -r requirements/doc.txt

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
run: install
	@echo "Starting application..."
#	$(PYTHON) src/app.py

# ------------------------------------------------------------
# TESTING
# ------------------------------------------------------------
test: install-dev
	@echo "Running tests with pytest..."
	$(PYTHON) -m pytest tests/ -v

test-coverage: install-dev
	@echo "Running tests with coverage..."
	$(PYTHON) -m pytest tests/ --cov=health_sensor_simulator --cov-report=term-missing --cov-report=html

# ------------------------------------------------------------
# DOCUMENTATION
# ------------------------------------------------------------
# Build both HTML and PDF documentation
docs: docs-html docs-pdf

docs-html: install-dev
	@echo "Building HTML documentation..."
	$(SPHINXBUILD) -M html "$(DOCSSOURCEDIR)" "$(DOCSBUILDDIR)" $(SPHINXOPTS)
	@echo "HTML documentation built in $(DOCSBUILDDIR)/html/"

docs-pdf: install-dev
	@echo "Building PDF documentation (requires LaTeX)..."
	$(SPHINXBUILD) -M latexpdf "$(DOCSSOURCEDIR)" "$(DOCSBUILDDIR)" $(SPHINXOPTS)
	@echo "PDF documentation built in $(DOCSBUILDDIR)/latex/"

docs-clean:
	rm -rf "$(DOCSBUILDDIR)"


# ------------------------------------------------------------
# DEPLOYMENT
# ------------------------------------------------------------
docker-build:
	@echo "Building Docker image..."
	docker build -t health-sensor-simulator .

docker-run:
	@echo "Running Docker container..."
	docker run -it --rm health-sensor-simulator

docker-remove:
	@echo "Removing Docker image..."
	docker image rm -f health-sensor-simulator

# ------------------------------------------------------------
# CLEAN & HELP
# ------------------------------------------------------------
clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf dist build *.egg-info
	find $(SRC) -type d -name "__pycache__" -print0 | xargs -0 rm -rf
	$(MAKE) docs-clean

# ------------------------------------------------------------
# HELP
# ------------------------------------------------------------
help:  ## Show this help message
	@echo "================= Usage =================";
	@echo
	@echo "Environment Setup:"
	@echo "  setup-venv     Creates a virtual environment"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo
	@echo "Run:"
	@echo "  run            Run the application"
	@echo
	@echo "Testing:"
	@echo "  test           Run tests"
	@echo "  test-coverage  Run tests with coverage"
	@echo
	@echo "Documentation:"
	@echo "  docs           Build HTML and PDF documentation"
	@echo "  docs-html      Build HTML documentation only"
	@echo "  docs-pdf       Build PDF documentation only"
	@echo "  docs-clean     Remove documentation build files"
	@echo
	@echo "Deployment:"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-run     Run Docker container"
	@echo "  docker-remove  Remove Docker image"
	@echo
	@echo "Clean:"
	@echo "  clean          Remove caches and build artifacts"
	@echo
	@echo "To display this help message, run 'make help'"