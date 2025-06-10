from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from redis_operations import RedisSessionManager
import os
import redis

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones_flask'

# Configurar Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

# Inicializar manejador de sesiones Redis
try:
    session_manager = RedisSessionManager(host=redis_host, port=redis_port)
    print(f"✅ Conectado a Redis en {redis_host}:{redis_port}")
except Exception as e:
    print(f"❌ Error conectando a Redis: {e}")
    session_manager = None

@app.route('/')
def index():
    """Página principal con interfaz para gestión de sesiones"""
    # Verificar estado de Redis
    redis_status = verificar_conexion_redis()
    return render_template('index.html', redis_status=redis_status)

@app.route('/api/health')
def health_check():
    """Endpoint para verificar el estado del sistema"""
    redis_status = verificar_conexion_redis()
    return jsonify({
        'status': 'ok' if redis_status['connected'] else 'error',
        'redis': redis_status,
        'host': redis_host,
        'port': redis_port
    })

def verificar_conexion_redis():
    """Verificar si Redis está disponible"""
    try:
        if session_manager:
            session_manager.redis_client.ping()
            return {'connected': True, 'message': 'Redis conectado correctamente'}
        else:
            return {'connected': False, 'message': 'Session manager no inicializado'}
    except redis.ConnectionError:
        return {'connected': False, 'message': 'No se puede conectar a Redis. ¿Está Redis ejecutándose?'}
    except Exception as e:
        return {'connected': False, 'message': f'Error de conexión: {str(e)}'}

@app.route('/crear_sesion', methods=['POST'])
def crear_sesion():
    """Endpoint para crear nueva sesión"""
    if not session_manager:
        flash('Error: Redis no está disponible. Verifica que el servicio esté ejecutándose.', 'error')
        return redirect(url_for('index'))
        
    try:
        user_id = request.form.get('user_id')
        username = request.form.get('username')
        email = request.form.get('email')
        
        if not all([user_id, username, email]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('index'))
            
        token = session_manager.crear_sesion(user_id, username, email)
        flash(f'Sesión creada exitosamente. Token: {token}', 'success')
        
    except redis.ConnectionError:
        flash('Error: No se puede conectar a Redis. Verifica que el servicio esté ejecutándose.', 'error')
    except Exception as e:
        flash(f'Error al crear sesión: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/obtener_sesion', methods=['POST'])
def obtener_sesion():
    """Endpoint para obtener información de sesión"""
    if not session_manager:
        flash('Error: Redis no está disponible. Verifica que el servicio esté ejecutándose.', 'error')
        return redirect(url_for('index'))
        
    try:
        token = request.form.get('session_token')
        if not token:
            flash('Token de sesión requerido', 'error')
            return redirect(url_for('index'))
            
        session_data = session_manager.obtener_sesion(token)
        if session_data:
            flash(f'Sesión encontrada: {session_data}', 'info')
        else:
            flash('Sesión no encontrada o expirada', 'warning')
            
    except redis.ConnectionError:
        flash('Error: No se puede conectar a Redis. Verifica que el servicio esté ejecutándose.', 'error')
    except Exception as e:
        flash(f'Error al obtener sesión: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/cerrar_sesion', methods=['POST'])
def cerrar_sesion():
    """Endpoint para cerrar sesión"""
    if not session_manager:
        flash('Error: Redis no está disponible. Verifica que el servicio esté ejecutándose.', 'error')
        return redirect(url_for('index'))
        
    try:
        token = request.form.get('session_token')
        if not token:
            flash('Token de sesión requerido', 'error')
            return redirect(url_for('index'))
            
        if session_manager.cerrar_sesion(token):
            flash('Sesión cerrada exitosamente', 'success')
        else:
            flash('Sesión no encontrada', 'warning')
            
    except redis.ConnectionError:
        flash('Error: No se puede conectar a Redis. Verifica que el servicio esté ejecutándose.', 'error')
    except Exception as e:
        flash(f'Error al cerrar sesión: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/api/estadisticas')
def api_estadisticas():
    """API endpoint para obtener estadísticas en tiempo real"""
    if not session_manager:
        return jsonify({'error': 'Redis no disponible'}), 503
        
    try:
        stats = session_manager.obtener_estadisticas()
        return jsonify(stats)
    except redis.ConnectionError:
        return jsonify({'error': 'No se puede conectar a Redis'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sesiones_activas')
def api_sesiones_activas():
    """API endpoint para listar sesiones activas"""
    if not session_manager:
        return jsonify({'error': 'Redis no disponible'}), 503
        
    try:
        sesiones = session_manager.listar_sesiones_activas()
        return jsonify(sesiones)
    except redis.ConnectionError:
        return jsonify({'error': 'No se puede conectar a Redis'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/limpiar_expiradas', methods=['POST'])
def limpiar_expiradas():
    """Endpoint para limpiar sesiones expiradas"""
    if not session_manager:
        flash('Error: Redis no está disponible. Verifica que el servicio esté ejecutándose.', 'error')
        return redirect(url_for('index'))
        
    try:
        count = session_manager.limpiar_sesiones_expiradas()
        flash(f'Limpieza completada. {count} sesiones procesadas', 'info')
    except redis.ConnectionError:
        flash('Error: No se puede conectar a Redis. Verifica que el servicio esté ejecutándose.', 'error')
    except Exception as e:
        flash(f'Error en limpieza: {str(e)}', 'error')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
