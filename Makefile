.PHONY: help build up down logs restart clean init-db test

help:
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - Show logs from all services"
	@echo "  make restart    - Restart all services"
	@echo "  make clean      - Remove all containers and volumes"
	@echo "  make init-db    - Initialize database with default data"
	@echo "  make shell      - Open shell in app container"
	@echo "  make test       - Run tests"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started! API available at http://localhost:8000"
	@echo "Docs available at http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	@echo "All containers and volumes removed"

init-db:
	docker-compose exec app python init_db.py

shell:
	docker-compose exec app /bin/bash

test:
	docker-compose exec app pytest
