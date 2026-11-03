from flask import Blueprint, request, jsonify, session
from backend.database import db
from backend.models import Usuario
from backend.config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    correo = data.get('correo', '').strip().lower()
    password = data.get('password', '')
    rol_solicitado = data.get('rol', 'cliente').strip().lower()
    codigo_admin = data.get('codigo_admin', '').strip()
    
    if not nombre or not correo or not password:
        return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400
        
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({'success': False, 'message': 'El correo electrónico ya está registrado'}), 409
        
    # Validación para creación de cuenta de Administrador / Dueño de Tienda
    rol_final = 'cliente'
    if rol_solicitado == 'administrador':
        clave_maestra = Config.ADMIN_REGISTRATION_KEY
        if codigo_admin != clave_maestra:
            return jsonify({
                'success': False, 
                'message': f'Código de autorización de propietario incorrecto. (Código por defecto para entrega: {clave_maestra})'
            }), 403
        rol_final = 'administrador'
        
    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        rol=rol_final,
        activo=True
    )
    nuevo_usuario.set_password(password)
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    # Iniciar sesión automáticamente
    session['id_usuario'] = nuevo_usuario.id_usuario
    session['rol'] = nuevo_usuario.rol
    session['nombre'] = nuevo_usuario.nombre
    
    mensaje_exito = '¡Cuenta de Administrador / Propietario creada exitosamente!' if rol_final == 'administrador' else '¡Cuenta de Cliente creada con éxito!'
    
    return jsonify({
        'success': True,
        'message': mensaje_exito,
        'usuario': nuevo_usuario.to_dict(),
        'redirect': '/admin' if rol_final == 'administrador' else '/catalogo'
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    correo = data.get('correo', '').strip().lower()
    password = data.get('password', '')
    portal_tipo = data.get('portal_tipo', 'cliente').strip().lower()  # 'cliente' o 'administrador'
    
    if not correo or not password:
        return jsonify({'success': False, 'message': 'Correo y contraseña requeridos'}), 400
        
    usuario = Usuario.query.filter_by(correo=correo).first()
    
    if not usuario or not usuario.check_password(password):
        return jsonify({'success': False, 'message': 'Credenciales inválidas. Verifica tu correo y contraseña.'}), 401
        
    if not usuario.activo:
        return jsonify({'success': False, 'message': 'Esta cuenta ha sido desactivada por el administrador'}), 403
        
    # Verificación de portal según rol
    if portal_tipo == 'administrador' and usuario.rol != 'administrador':
        return jsonify({
            'success': False,
            'message': 'Esta cuenta pertenece a un Cliente. Por favor ingresa a través del Portal de Clientes o registra una cuenta de Administrador con el código de propietario.'
        }), 403
        
    session['id_usuario'] = usuario.id_usuario
    session['rol'] = usuario.rol
    session['nombre'] = usuario.nombre
    
    return jsonify({
        'success': True,
        'message': f'¡Bienvenido(a), {usuario.nombre}!',
        'usuario': usuario.to_dict(),
        'redirect': '/admin' if usuario.rol == 'administrador' else '/catalogo'
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Sesión cerrada exitosamente'})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('id_usuario')
    if not user_id:
        return jsonify({'authenticated': False}), 200
        
    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.activo:
        session.clear()
        return jsonify({'authenticated': False}), 200
        
    return jsonify({
        'authenticated': True,
        'usuario': usuario.to_dict()
    })
