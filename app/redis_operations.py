import redis
import json
import time
import uuid
from datetime import datetime, timedelta

class RedisSessionManager:
    def __init__(self, host='redis', port=6379, db=0):
        """Inicializar conexión a Redis"""
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            decode_responses=True
        )
        
    def crear_sesion(self, user_id, username, email):
        """
        Crear una nueva sesión de usuario
        Patrón de clave: session:{token}
        Tipo de dato: Hash
        """
        session_token = str(uuid.uuid4())
        session_key = f"session:{session_token}"
        
        # Datos de la sesión como hash
        session_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        # Almacenar sesión con expiración de 1 hora
        self.redis_client.hset(session_key, mapping=session_data)
        self.redis_client.expire(session_key, 3600)  # 1 hora TTL
        
        # Incrementar contador de sesiones activas
        self.redis_client.incr('stats:active_sessions')
        
        # Actualizar perfil de usuario
        self.actualizar_perfil_usuario(user_id, username, email)
        
        # Agregar a ranking de usuarios activos
        self.redis_client.zadd('ranking:active_users', {user_id: time.time()})
        
        return session_token
        
    def obtener_sesion(self, session_token):
        """
        Obtener información de una sesión
        Comando: HGETALL
        """
        session_key = f"session:{session_token}"
        session_data = self.redis_client.hgetall(session_key)
        
        if session_data:
            # Actualizar última actividad
            self.redis_client.hset(session_key, 'last_activity', datetime.now().isoformat())
            return session_data
        return None
        
    def actualizar_perfil_usuario(self, user_id, username, email):
        """
        Actualizar perfil de usuario
        Patrón: user:{user_id}:profile
        Tipo: Hash
        """
        profile_key = f"user:{user_id}:profile"
        profile_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'updated_at': datetime.now().isoformat()
        }
        self.redis_client.hset(profile_key, mapping=profile_data)
        
    def cerrar_sesion(self, session_token):
        """
        Cerrar sesión eliminando el token
        Comando: DEL
        """
        session_key = f"session:{session_token}"
        
        # Verificar si existe antes de eliminar
        if self.redis_client.exists(session_key):
            # Obtener user_id antes de eliminar
            user_id = self.redis_client.hget(session_key, 'user_id')
            
            # Eliminar sesión
            self.redis_client.delete(session_key)
            
            # Decrementar contador
            current_sessions = self.redis_client.get('stats:active_sessions')
            if current_sessions and int(current_sessions) > 0:
                self.redis_client.decr('stats:active_sessions')
                
            # Remover del ranking
            if user_id:
                self.redis_client.zrem('ranking:active_users', user_id)
                
            return True
        return False
        
    def obtener_estadisticas(self):
        """
        Obtener estadísticas del sistema
        Comandos: GET, ZCARD, ZRANGE
        """
        stats = {
            'sesiones_activas': self.redis_client.get('stats:active_sessions') or '0',
            'usuarios_en_ranking': self.redis_client.zcard('ranking:active_users'),
            'usuarios_recientes': self.redis_client.zrange('ranking:active_users', -5, -1, withscores=True)
        }
        return stats
        
    def listar_sesiones_activas(self):
        """
        Listar todas las sesiones activas
        Comando: SCAN con patrón
        """
        sesiones = []
        for key in self.redis_client.scan_iter(match="session:*"):
            session_data = self.redis_client.hgetall(key)
            if session_data:
                session_data['token'] = key.split(':')[1]
                session_data['ttl'] = self.redis_client.ttl(key)
                sesiones.append(session_data)
        return sesiones
        
    def limpiar_sesiones_expiradas(self):
        """
        Limpiar sesiones expiradas manualmente
        Útil para demostración
        """
        count = 0
        for key in self.redis_client.scan_iter(match="session:*"):
            ttl = self.redis_client.ttl(key)
            if ttl == -1:  # Sin expiración
                self.redis_client.expire(key, 3600)
            elif ttl == -2:  # Clave no existe
                count += 1
        return count
