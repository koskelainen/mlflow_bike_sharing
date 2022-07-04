ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_FILE := $(ROOT_DIR)/docker-compose.yml

VENV_NAME := venv
VENV_PATH := ${ROOT_DIR}/${VENV_NAME}

# Variable for the python command (later overwritten if not working)
PYTHON_INTERPRETER := python

# Get version string (e.g. Python 3.7.1)
PYTHON_VERSION_STRING := $(shell $(PYTHON_INTERPRETER) -V)

# If PYTHON_VERSION_STRING is empty there probably isn't any 'python'
# on PATH, and you should try set it using 'python3' (or python2) instead.
ifndef PYTHON_VERSION_STRING
    PYTHON_INTERPRETER := python3
    PYTHON_VERSION_STRING := $(shell $(PYTHON_INTERPRETER) -V)
	ifndef PYTHON_VERSION_STRING
		$(error No python interpreter found on PATH)
	endif
endif

# Split components (changing "." into " ")
PYTHON_VERSION_TOKENS := $(subst ., ,$(PYTHON_VERSION_STRING)) # Python 3 7 1
PYTHON_MAJOR_VERSION := $(word 2,$(PYTHON_VERSION_TOKENS)) # 3
PYTHON_MINOR_VERSION := $(word 3,$(PYTHON_VERSION_TOKENS)) # 4


.DEFAULT_GOAL := help

.PHONY: build
build: ## Build all or c=<name> container
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) build $(c)

.PHONY: rebuild
rebuild: down build start## Stop containers (via 'down'), rebuilds services images (via 'build') and start services (via 'start')

.PHONY: up
up: ## Start all or c=<name> containers in foreground
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up $(c)

.PHONY: start
start: ## Start all or c=<name> containers in background
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d $(c)

.PHONY: stop
stop: ## Stop all or c=<name> containers
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) stop $(c)

.PHONY: restart
restart: ## Restart all or c=<name> containers
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) stop $(c)
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d $(c)

.PHONY: logs
logs: ## Show logs for all or c=<name> containers
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs --tail=100 -f $(c)

.PHONY: status
status: ## Show status of containers
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

.PHONY: ps
ps: status ## Alias of status

.PHONY: down
down: confirm ## Clean all data
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

.PHONY: clean
clean: down ## Clean all data

.PHONY: confirm
confirm:
	@( read -p "$(RED)Are you sure? [y/N]$(RESET): " sure && case "$$sure" in [yY]) true;; *) false;; esac )

.PHONY: lint
lint: ## Lint using flake8
	flake8 src

.PHONY: dirs
dirs: ## Create symlink and directories that are ignored by git but required for the project
	ln -sf config/.env
	mkdir -p data/raw data/processed data/dc_volumes data/experiments models

.PHONY: dataset
dataset: ## Download Bike Sharing Dataset
	wget -P data/raw/ "http://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip"
	cd data/raw/ && unzip -o "Bike-Sharing-Dataset.zip" && cd ${ROOT_DIR}

.PHONY: dvcrun
dvcrun: ## Start dvc pipline
	dvc repro prepare_configs -f
	dvc repro prepare_dataset -f
	dvc repro split_dataset -f
	dvc repro train -f
	dvc repro model_select -f

.PHONY: venv
venv: ## Create virtualenv and ctivate it
	$(PYTHON_INTERPRETER) -m venv ${VENV_PATH}
	@echo Activate with the command:
	@echo source ./${VENV_NAME}/bin/activate

.PHONY: requirements
requirements: ## Install Python Dependencies. Make sure you activate the virtualenv first!
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

.PHONY: demo
demo: dirs requirements dataset start dvcrun ## Just run all steps prepare, get model and run api endpoints

.PHONY: help
help: ## Show help
	@echo Please specify a build target. The choices are:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
