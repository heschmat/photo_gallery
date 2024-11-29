# Variables
DOCKER_COMPOSE=docker compose
SERVICE=web

# Commands
makemigrations:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) sh -c "python manage.py makemigrations"

createsuperuser:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) sh -c "python manage.py createsuperuser"

test:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) sh -c "python manage.py test"

lint:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) flake8

down:
	$(DOCKER_COMPOSE) down --volumes

up:
	$(DOCKER_COMPOSE) up

# Default target
.PHONY: all
all: makemigrations createsuperuser test lint
