#!/bin/bash

echo "🚀 Iniciando ESCOM BDA Práctica 9 - Redis Key-Value Database"
echo "============================================================"

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose no está instalado"
    echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

# Verificar que Docker esté ejecutándose
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker no está ejecutándose"
    echo "Inicia Docker y vuelve a intentar"
    exit 1
fi

echo "✅ Docker verificado correctamente"

# Detener servicios existentes si están ejecutándose
echo "🔄 Deteniendo servicios existentes..."
docker-compose down

# Construir y levantar servicios
echo "🏗️  Construyendo y levantando servicios..."
docker-compose up --build -d

# Esperar a que Redis esté listo
echo "⏳ Esperando a que Redis esté listo..."
sleep 5

# Verificar que Redis esté funcionando
echo "🔍 Verificando conexión a Redis..."
if docker exec escom_bda_redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis está funcionando correctamente"
else
    echo "❌ Error: Redis no responde"
    echo "📋 Logs de Redis:"
    docker logs escom_bda_redis
    exit 1
fi

# Verificar que la aplicación web esté funcionando
echo "🔍 Verificando aplicación web..."
sleep 3
if curl -s http://localhost:5000/api/health | grep -q "ok"; then
    echo "✅ Aplicación web funcionando correctamente"
else
    echo "⚠️  La aplicación web puede estar iniciándose aún..."
fi

echo ""
echo "🎉 ¡Servicios iniciados exitosamente!"
echo "============================================"
echo ""
echo "📊 URLs disponibles:"
echo "   • Aplicación web: http://localhost:5000"
echo "   • Health check:   http://localhost:5000/api/health"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver logs:           docker-compose logs -f"
echo "   • Redis CLI:          docker exec -it escom_bda_redis redis-cli"
echo "   • Entrar al app:      docker exec -it escom_bda_app bash"
echo "   • Demo Redis:         docker exec -it escom_bda_app python scripts/demo_redis.py"
echo "   • Detener servicios:  docker-compose down"
echo ""
echo "📋 Estado de servicios:"
docker-compose ps
