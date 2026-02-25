# ==============================================================================
# Makefile - Comandos útiles del proyecto
# ==============================================================================
#
# Uso:
#   make help        - Mostrar ayuda
#   make build       - Construir imágenes Docker
#   make up          - Levantar servicios
#   make down        - Bajar servicios
#   make test        - Ejecutar tests
#
# ==============================================================================

.PHONY: help build up down restart logs clean test lint migrate backup

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.prod.yml
BACKEND_CONTAINER = minimum_api_backend
FRONTEND_CONTAINER = minimum_api_frontend

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help: ## Mostrar ayuda
	@echo "$(GREEN)Comandos disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ==============================================================================
# Docker
# ==============================================================================

build: ## Construir imágenes Docker
	@echo "$(GREEN)🔨 Construyendo imágenes...$(NC)"
	$(DOCKER_COMPOSE) build

up: ## Levantar servicios en desarrollo
	@echo "$(GREEN)🚀 Levantando servicios...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Servicios corriendo$(NC)"
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "Swagger:  http://localhost:8000/api/docs/"

down: ## Bajar servicios
	@echo "$(YELLOW)🛑 Bajando servicios...$(NC)"
	$(DOCKER_COMPOSE) down

restart: down up ## Reiniciar servicios

logs: ## Ver logs de todos los servicios
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## Ver logs del backend
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## Ver logs del frontend
	$(DOCKER_COMPOSE) logs -f frontend

clean: ## Limpiar contenedores, volúmenes e imágenes
	@echo "$(YELLOW)🧹 Limpiando...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f

# ==============================================================================
# Desarrollo
# ==============================================================================

shell-backend: ## Abrir shell en el backend
	docker exec -it $(BACKEND_CONTAINER) bash

shell-frontend: ## Abrir shell en el frontend
	docker exec -it $(FRONTEND_CONTAINER) sh

shell-db: ## Abrir shell de PostgreSQL
	docker exec -it minimum_api_db psql -U postgres -d minimum_api

# ==============================================================================
# Backend
# ==============================================================================

migrate: ## Ejecutar migraciones
	@echo "$(GREEN)📦 Ejecutando migraciones...$(NC)"
	docker exec $(BACKEND_CONTAINER) python manage.py migrate

makemigrations: ## Crear migraciones
	@echo "$(GREEN)📝 Creando migraciones...$(NC)"
	docker exec $(BACKEND_CONTAINER) python manage.py makemigrations

superuser: ## Crear superusuario
	docker exec -it $(BACKEND_CONTAINER) python manage.py createsuperuser

seed: ## Seed de roles y permisos
	docker exec $(BACKEND_CONTAINER) python manage.py seed_roles

collectstatic: ## Recolectar archivos estáticos
	docker exec $(BACKEND_CONTAINER) python manage.py collectstatic --noinput

# ==============================================================================
# Testing
# ==============================================================================

test: ## Ejecutar todos los tests del backend
	@echo "$(GREEN)🧪 Ejecutando tests...$(NC)"
	docker exec $(BACKEND_CONTAINER) python manage.py test

test-coverage: ## Ejecutar tests con coverage
	@echo "$(GREEN)🧪 Ejecutando tests con coverage...$(NC)"
	docker exec $(BACKEND_CONTAINER) pytest --cov=apps --cov-report=html

test-frontend: ## Ejecutar tests del frontend
	@echo "$(GREEN)🧪 Ejecutando tests del frontend...$(NC)"
	docker exec $(FRONTEND_CONTAINER) npm test

# ==============================================================================
# Linting
# ==============================================================================

lint-backend: ## Ejecutar linter en backend
	@echo "$(GREEN)🔍 Ejecutando linter backend...$(NC)"
	docker exec $(BACKEND_CONTAINER) flake8 apps/

lint-frontend: ## Ejecutar linter en frontend
	@echo "$(GREEN)🔍 Ejecutando linter frontend...$(NC)"
	docker exec $(FRONTEND_CONTAINER) npm run lint

lint: lint-backend lint-frontend ## Ejecutar todos los linters

format-backend: ## Formatear código backend con black
	docker exec $(BACKEND_CONTAINER) black apps/

# ==============================================================================
# Backup y Restore
# ==============================================================================

backup: ## Crear backup de la base de datos
	@echo "$(GREEN)💾 Creando backup...$(NC)"
	./scripts/backup_db.sh

restore: ## Restaurar backup de la base de datos
	@echo "$(YELLOW)📥 Restaurando backup...$(NC)"
	@echo "Uso: make restore FILE=backups/backup_YYYYMMDD_HHMMSS.sql.gz"
	@if [ -z "$(FILE)" ]; then echo "Error: Especifica FILE=ruta/archivo"; exit 1; fi
	gunzip -c $(FILE) | docker exec -i minimum_api_db psql -U postgres -d minimum_api

# ==============================================================================
# Producción
# ==============================================================================

build-prod: ## Construir imágenes para producción
	@echo "$(GREEN)🔨 Construyendo imágenes de producción...$(NC)"
	$(DOCKER_COMPOSE_PROD) build

up-prod: ## Levantar servicios en producción
	@echo "$(GREEN)🚀 Levantando servicios de producción...$(NC)"
	$(DOCKER_COMPOSE_PROD) up -d

down-prod: ## Bajar servicios de producción
	$(DOCKER_COMPOSE_PROD) down

# ==============================================================================
# Instalación inicial
# ==============================================================================

install: build up migrate seed superuser ## Instalación completa desde cero
	@echo "$(GREEN)✅ Instalación completada$(NC)"
	@echo ""
	@echo "Accesos:"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:5173"
	@echo "  Swagger:  http://localhost:8000/api/docs/"
	@echo ""
	@echo "Credenciales:"
	@echo "  Usuario:  admin"
	@echo "  Password: admin"