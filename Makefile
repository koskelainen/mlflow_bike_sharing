ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_FILE := $(ROOT_DIR)/docker-compose.yml


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
dirs: ## Create directories that are ignored by git but required for the project
	mkdir -p data/raw data/processed data/dc_volumes data/experiments models

.PHONY: dataset
dataset: ## Download Bike Sharing Dataset
	wget -P data/raw/ "http://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip"
	cd data/raw/ && unzip -o "Bike-Sharing-Dataset.zip" && cd ${ROOT_DIR}

.PHONY: dvcrun
dvcrun: ## Start evaluate dvc pipeline
	dvc repro


.PHONY: help
help: ## Show help
	@echo Please specify a build target. The choices are:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
