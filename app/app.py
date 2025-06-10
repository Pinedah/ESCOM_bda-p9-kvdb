from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from redis_operations import RedisSessionManager
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones_flask'

# Configurar Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

# Inicializar manejador de sesiones Redis
session_manager = RedisSessionManager(host=redis_host, port=redis_port)

@app.route('/')
def index():
    """Página principal con interfaz para gestión de sesiones"""
    return render_template('index.html')

@app.route('/crear_sesion', methods=['POST'])
def crear_sesion():
    """Endpoint para crear nueva sesión"""
    try:
        user_id = request.form.get('user_id')
        username = request.form.get('username')
        email = request.form.get('email')
        
        if not all([user_id, username, email]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('index'))
            
        token = session_manager.crear_sesion(user_id, username, email)
        flash(f'Sesión creada exitosamente. Token: {token}', 'success')
        
    except Exception as e:
        flash(f'Error al crear sesión: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/obtener_sesion', methods=['POST'])
def obtener_sesion():
    """Endpoint para obtener información de sesión"""
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
            
    except Exception as e:
        flash(f'Error al obtener sesión: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/cerrar_sesion', methods=['POST'])
def cerrar_sesion():
    """Endpoint para cerrar sesión"""
    try:
        token = request.form.get('session_token')
        if not token:
            flash('Token de sesión requerido', 'error')
            return redirect(url_for('index'))
            
        if session_manager.cerrar_sesion(token):
            flash('Sesión cerrada exitosamente', 'success')
        else:
            flash('Sesión no encontrada', 'warning')
            
    except Exception as e:
        flash(f'Error al cerrar sesión: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/api/estadisticas')
def api_estadisticas():
    """API endpoint para obtener estadísticas en tiempo real"""
    try:
        stats = session_manager.obtener_estadisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sesiones_activas')
def api_sesiones_activas():
    """API endpoint para listar sesiones activas"""
    try:
        sesiones = session_manager.listar_sesiones_activas()
        return jsonify(sesiones)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/limpiar_expiradas', methods=['POST'])
def limpiar_expiradas():
    """Endpoint para limpiar sesiones expiradas"""
    try:
        count = session_manager.limpiar_sesiones_expiradas()
        flash(f'Limpieza completada. {count} sesiones procesadas', 'info')
    except Exception as e:
        flash(f'Error en limpieza: {str(e)}', 'error')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
