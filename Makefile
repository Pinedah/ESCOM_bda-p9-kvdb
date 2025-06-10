# Variables
PROJECT_NAME = escom_bda_p9_kvdb
REDIS_CONTAINER = escom_bda_redis
APP_CONTAINER = escom_bda_app

.PHONY: help start stop restart logs redis-cli demo health status clean

# Comando por defecto
help:
	@echo "🔴 ESCOM BDA Práctica 9 - Redis Key-Value Database"
	@echo "=================================================="
	@echo ""
	@echo "Comandos disponibles:"
	@echo "  start       - Iniciar todos los servicios"
	@echo "  stop        - Detener todos los servicios"
	@echo "  restart     - Reiniciar todos los servicios"
	@echo "  logs        - Ver logs de todos los servicios"
	@echo "  redis-cli   - Conectar a Redis CLI"
	@echo "  demo        - Ejecutar script de demostración"
	@echo "  health      - Verificar estado de servicios"
	@echo "  status      - Ver estado de contenedores"
	@echo "  clean       - Limpiar contenedores y volúmenes"
	@echo ""

# Iniciar servicios
start:
	@echo "🚀 Iniciando servicios..."
	@chmod +x start.sh
	@./start.sh

# Detener servicios
stop:
	@echo "🛑 Deteniendo servicios..."
	docker-compose down

# Reiniciar servicios
restart: stop start

# Ver logs
logs:
	@echo "📋 Mostrando logs de servicios..."
	docker-compose logs -f

# Conectar a Redis CLI
redis-cli:
	@echo "🔴 Conectando a Redis CLI..."
	@echo "Comandos útiles: PING, KEYS *, INFO, MONITOR"
	docker exec -it $(REDIS_CONTAINER) redis-cli

# Ejecutar demostración
demo:
	@echo "🎭 Ejecutando demostración de Redis..."
	docker exec -it $(APP_CONTAINER) python scripts/demo_redis.py

# Verificar estado
health:
	@echo "🏥 Verificando estado de servicios..."
	@echo ""
	@echo "Redis ping:"
	@docker exec $(REDIS_CONTAINER) redis-cli ping 2>/dev/null || echo "❌ Redis no responde"
	@echo ""
	@echo "Aplicación web:"
	@curl -s http://localhost:5000/api/health | jq . 2>/dev/null || echo "❌ App no responde"

# Estado de contenedores
status:
	@echo "📊 Estado de contenedores:"
	docker-compose ps

# Limpiar todo
clean:
	@echo "🧹 Limpiando contenedores y volúmenes..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Comandos de desarrollo
build:
	@echo "🏗️  Construyendo imágenes..."
	docker-compose build

shell-app:
	@echo "🐚 Entrando al contenedor de aplicación..."
	docker exec -it $(APP_CONTAINER) bash

shell-redis:
	@echo "🐚 Entrando al contenedor de Redis..."
	docker exec -it $(REDIS_CONTAINER) sh

# Comandos de testing
test-redis:
	@echo "🧪 Ejecutando pruebas de Redis..."
	docker exec -it $(REDIS_CONTAINER) sh /scripts/test_commands.sh

# Monitoreo
monitor:
	@echo "👁️  Monitoreando Redis en tiempo real..."
	docker exec -it $(REDIS_CONTAINER) redis-cli monitor

# Información del sistema
info:
	@echo "ℹ️  Información del sistema Redis:"
	docker exec -it $(REDIS_CONTAINER) redis-cli info
