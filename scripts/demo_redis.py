#!/usr/bin/env python3
"""
Script de demostración de operaciones Redis
Práctica 9: Bases de Datos Clave-Valor
ESCOM - Bases de Datos Avanzadas
"""

import redis
import time
import json
from datetime import datetime

def conectar_redis():
    """Establecer conexión con Redis"""
    try:
        r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✅ Conexión exitosa a Redis")
        return r
    except Exception as e:
        print(f"❌ Error conectando a Redis: {e}")
        return None

def demostrar_comandos_basicos(r):
    """Demostrar comandos básicos de Redis"""
    print("\n" + "="*50)
    print("📝 DEMOSTRACIÓN DE COMANDOS BÁSICOS")
    print("="*50)
    
    # SET y GET
    print("\n1. Operaciones SET/GET:")
    r.set("ejemplo:clave", "valor_de_prueba")
    valor = r.get("ejemplo:clave")
    print(f"   SET ejemplo:clave → 'valor_de_prueba'")
    print(f"   GET ejemplo:clave → '{valor}'")
    
    # INCR y DECR
    print("\n2. Contadores INCR/DECR:")
    r.set("contador", 0)
    r.incr("contador")
    r.incr("contador", 5)
    contador = r.get("contador")
    print(f"   INCR contador → {contador}")
    
    # EXPIRE y TTL
    print("\n3. Expiración EXPIRE/TTL:")
    r.set("temporal", "valor_temporal")
    r.expire("temporal", 10)
    ttl = r.ttl("temporal")
    print(f"   EXPIRE temporal 10 → TTL: {ttl} segundos")
    
    # HSET y HGETALL
    print("\n4. Hashes HSET/HGETALL:")
    usuario_data = {
        "nombre": "Juan Pérez",
        "email": "juan@ejemplo.com",
        "edad": "25"
    }
    r.hset("usuario:123", mapping=usuario_data)
    usuario = r.hgetall("usuario:123")
    print(f"   HSET usuario:123 → {usuario}")
    
    # LPUSH y LRANGE
    print("\n5. Listas LPUSH/LRANGE:")
    r.lpush("tareas", "tarea1", "tarea2", "tarea3")
    tareas = r.lrange("tareas", 0, -1)
    print(f"   LPUSH tareas → {tareas}")
    
    # ZADD y ZRANGE
    print("\n6. Sorted Sets ZADD/ZRANGE:")
    r.zadd("puntuaciones", {"jugador1": 100, "jugador2": 150, "jugador3": 120})
    ranking = r.zrange("puntuaciones", 0, -1, withscores=True)
    print(f"   ZADD puntuaciones → {ranking}")

def demostrar_caso_uso_sesiones(r):
    """Demostrar el caso de uso específico: gestión de sesiones"""
    print("\n" + "="*50)
    print("🎯 CASO DE USO: GESTIÓN DE SESIONES")
    print("="*50)
    
    # Simular múltiples usuarios creando sesiones
    usuarios = [
        {"id": "user_001", "nombre": "Ana García", "email": "ana@ejemplo.com"},
        {"id": "user_002", "nombre": "Carlos López", "email": "carlos@ejemplo.com"},
        {"id": "user_003", "nombre": "María Rodríguez", "email": "maria@ejemplo.com"}
    ]
    
    tokens_creados = []
    
    print("\n1. Creando sesiones de usuario:")
    for usuario in usuarios:
        # Generar token simple para demo
        token = f"session_{usuario['id']}_{int(time.time())}"
        session_key = f"session:{token}"
        
        # Crear datos de sesión
        session_data = {
            "user_id": usuario["id"],
            "username": usuario["nombre"],
            "email": usuario["email"],
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Almacenar sesión con TTL
        r.hset(session_key, mapping=session_data)
        r.expire(session_key, 300)  # 5 minutos
        
        # Incrementar contador
        r.incr("stats:active_sessions")
        
        # Agregar a ranking
        r.zadd("ranking:active_users", {usuario["id"]: time.time()})
        
        tokens_creados.append(token)
        print(f"   ✅ Sesión creada para {usuario['nombre']} → Token: {token[:20]}...")
    
    print(f"\n2. Sesiones activas: {r.get('stats:active_sessions')}")
    
    print("\n3. Consultando sesiones:")
    for i, token in enumerate(tokens_creados[:2]):  # Solo mostrar 2
        session_key = f"session:{token}"
        session_data = r.hgetall(session_key)
        ttl = r.ttl(session_key)
        print(f"   📋 Sesión {i+1}: {session_data['username']} (TTL: {ttl}s)")
    
    print("\n4. Ranking de usuarios activos:")
    ranking = r.zrange("ranking:active_users", 0, -1, withscores=True)
    for user_id, timestamp in ranking:
        print(f"   🏆 {user_id} → Última actividad: {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}")
    
    # Simular cierre de sesión
    print("\n5. Cerrando una sesión:")
    token_a_cerrar = tokens_creados[0]
    session_key = f"session:{token_a_cerrar}"
    user_id = r.hget(session_key, "user_id")
    
    r.delete(session_key)
    r.decr("stats:active_sessions")
    r.zrem("ranking:active_users", user_id)
    
    print(f"   ❌ Sesión cerrada para {user_id}")
    print(f"   📊 Sesiones activas restantes: {r.get('stats:active_sessions')}")

def demostrar_estructuras_datos(r):
    """Demostrar diferentes estructuras de datos de Redis"""
    print("\n" + "="*50)
    print("🏗️  ESTRUCTURAS DE DATOS REDIS")
    print("="*50)
    
    # Limpiar datos previos
    for key in r.scan_iter(match="demo:*"):
        r.delete(key)
    
    print("\n1. Strings - Configuración de aplicación:")
    configs = {
        "demo:config:timeout": "30",
        "demo:config:max_connections": "100",
        "demo:config:debug_mode": "true"
    }
    for key, value in configs.items():
        r.set(key, value)
        print(f"   {key} = {value}")
    
    print("\n2. Lists - Cola de tareas:")
    tareas = ["procesar_pedido_001", "enviar_email_usuario_123", "generar_reporte_ventas"]
    for tarea in tareas:
        r.lpush("demo:cola_tareas", tarea)
    
    print(f"   Cola actual: {r.lrange('demo:cola_tareas', 0, -1)}")
    print(f"   Procesando: {r.rpop('demo:cola_tareas')}")
    
    print("\n3. Sets - Etiquetas de productos:")
    r.sadd("demo:producto:123:tags", "electronico", "portatil", "oferta")
    r.sadd("demo:producto:456:tags", "electronico", "gaming", "nuevo")
    
    tags_123 = r.smembers("demo:producto:123:tags")
    tags_456 = r.smembers("demo:producto:456:tags")
    tags_comunes = r.sinter("demo:producto:123:tags", "demo:producto:456:tags")
    
    print(f"   Producto 123 tags: {tags_123}")
    print(f"   Producto 456 tags: {tags_456}")
    print(f"   Tags en común: {tags_comunes}")
    
    print("\n4. Sorted Sets - Leaderboard de juego:")
    puntuaciones = {
        "player_alpha": 1500,
        "player_beta": 1200,
        "player_gamma": 1800,
        "player_delta": 1350
    }
    r.zadd("demo:leaderboard", puntuaciones)
    
    top_3 = r.zrange("demo:leaderboard", -3, -1, withscores=True)
    print("   Top 3 jugadores:")
    for i, (jugador, puntos) in enumerate(reversed(top_3), 1):
        print(f"   {i}. {jugador}: {int(puntos)} puntos")

def mostrar_informacion_sistema(r):
    """Mostrar información del sistema Redis"""
    print("\n" + "="*50)
    print("ℹ️  INFORMACIÓN DEL SISTEMA")
    print("="*50)
    
    info = r.info()
    print(f"Versión Redis: {info['redis_version']}")
    print(f"Modo de funcionamiento: {info['redis_mode']}")
    print(f"Claves en DB 0: {r.dbsize()}")
    print(f"Memoria usada: {info['used_memory_human']}")
    print(f"Conexiones totales: {info['total_connections_received']}")
    print(f"Comandos procesados: {info['total_commands_processed']}")

def main():
    """Función principal del script de demostración"""
    print("🔴 REDIS - DEMOSTRACIÓN DE OPERACIONES")
    print("Práctica 9: Bases de Datos Clave-Valor")
    print("ESCOM - Bases de Datos Avanzadas")
    print("=" * 60)
    
    # Conectar a Redis
    r = conectar_redis()
    if not r:
        return
    
    try:
        # Ejecutar demostraciones
        demostrar_comandos_basicos(r)
        demostrar_caso_uso_sesiones(r)
        demostrar_estructuras_datos(r)
        mostrar_informacion_sistema(r)
        
        print("\n" + "="*50)
        print("✅ DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*50)
        print("\n💡 Sugerencias para continuar:")
        print("   • Accede a redis-cli: docker exec -it escom_bda_redis redis-cli")
        print("   • Ve la aplicación web: http://localhost:5000")
        print("   • Revisa los logs: docker-compose logs redis")
        
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")

if __name__ == "__main__":
    main()
