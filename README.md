# ESCOM_bda-p9-kvdb
# Práctica 9: Bases de Datos Clave-Valor con Redis

## Descripción del Proyecto
Este proyecto implementa un sistema de gestión de sesiones de usuario utilizando Redis como base de datos Clave-Valor, con Docker para el entorno de desarrollo y una interfaz web simple.

## Caso de Uso: Sistema de Gestión de Sesiones
**Escenario elegido:** Gestión de información de sesiones de usuario para una aplicación web.

**Justificación:** Redis es ideal para este escenario porque:
- **Rendimiento:** Acceso rápido en memoria para consultas frecuentes de sesión
- **Expiración automática:** TTL (Time To Live) para sesiones que expiran
- **Escalabilidad:** Manejo eficiente de múltiples sesiones concurrentes
- **Simplicidad:** Estructura clave-valor perfecta para tokens de sesión

## Estructura del Proyecto
```
ESCOM_bda-p9-kvdb/
├── docker-compose.yml          # Configuración de servicios Docker
├── app/
│   ├── app.py                 # Aplicación Flask principal
│   ├── redis_operations.py    # Operaciones Redis
│   └── templates/
│       └── index.html         # Interfaz web
├── scripts/
│   ├── demo_redis.py          # Script de demostración
│   └── test_commands.sh       # Comandos de prueba Redis CLI
└── README.md
```

## Diseño de Claves y Valores

### Patrones de Claves:
- `session:{token}` - Información de sesión de usuario
- `user:{user_id}:profile` - Perfil básico de usuario
- `stats:active_sessions` - Contador de sesiones activas
- `user:{user_id}:last_activity` - Timestamp última actividad

### Tipos de Datos Redis Utilizados:
1. **Strings:** Para tokens de sesión y contadores
2. **Hashes:** Para perfiles de usuario y datos de sesión
3. **Sorted Sets:** Para ranking de usuarios activos

## Configuración y Ejecución

### Prerrequisitos
- Docker y Docker Compose instalados

### Pasos para ejecutar:

1. **Clonar y navegar al proyecto:**
```bash
cd /home/pineda/GitHub/ESCOM_bda-p9-kvdb
```

2. **Levantar los servicios:**
```bash
docker-compose up -d
```

3. **Verificar que Redis esté funcionando:**
```bash
docker ps
docker-compose logs redis
```

4. **Acceder a la aplicación web:**
```
http://localhost:5000
```

5. **Conectar a Redis CLI:**
```bash
docker exec -it escom_bda_redis redis-cli
```

## Comandos Redis Implementados

### Comandos Básicos Demostrados:
- `SET/GET` - Almacenar/recuperar valores simples
- `HSET/HGETALL` - Operaciones con hashes
- `INCR/DECR` - Contadores
- `EXPIRE/TTL` - Manejo de expiración
- `DEL` - Eliminación de claves
- `ZADD/ZRANGE` - Sorted sets para rankings

## Demostración de Funcionamiento

### 1. Usando la Interfaz Web:
- Crear sesiones de usuario
- Ver información de sesión
- Listar usuarios activos
- Estadísticas en tiempo real

### 2. Usando Redis CLI:
```bash
# Ejecutar script de pruebas
docker exec -it escom_bda_redis sh /scripts/test_commands.sh
```

### 3. Usando Script Python:
```bash
docker exec -it escom_bda_app python scripts/demo_redis.py
```

## Ventajas Observadas de Redis
1. **Velocidad:** Operaciones en memoria extremadamente rápidas
2. **Simplicidad:** API sencilla y directa
3. **Flexibilidad:** Múltiples tipos de datos
4. **Escalabilidad:** Manejo eficiente de concurrencia
5. **Persistencia:** Opcional para datos críticos

## Casos de Uso Adicionales Identificados
1. **Caché de consultas:** Almacenar resultados de queries costosas
2. **Contadores en tiempo real:** Estadísticas y métricas
3. **Colas de trabajo:** Lista de tareas pendientes
4. **Almacén de configuración:** Settings de aplicación
