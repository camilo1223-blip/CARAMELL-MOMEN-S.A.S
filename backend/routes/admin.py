from flask import Blueprint, request, jsonify, session
from datetime import datetime
from functools import wraps
from sqlalchemy import func
from backend.database import db
from backend.models import Usuario, Producto, Categoria, Pedido, DetallePedido, MovimientoInventario, Pago, Venta

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('id_usuario')
        rol = session.get('rol')
        if not user_id or rol != 'administrador':
            return jsonify({'success': False, 'message': 'Acceso denegado: se requieren permisos de administrador'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==================== PRODUCTOS ====================

@admin_bp.route('/productos', methods=['POST'])
@admin_required
def crear_producto():
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    id_categoria = data.get('id_categoria')
    precio = data.get('precio')
    stock = data.get('stock', 0)
    descripcion = data.get('descripcion', '').strip()
    imagen_url = data.get('imagen_url', '').strip()
    
    if not nombre or not id_categoria or precio is None:
        return jsonify({'success': False, 'message': 'Nombre, categoría y precio son obligatorios'}), 400
        
    try:
        precio = float(precio)
        stock = int(stock)
    except ValueError:
        return jsonify({'success': False, 'message': 'Precio o stock inválidos'}), 400
        
    prod = Producto(
        id_categoria=id_categoria,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        imagen_url=imagen_url,
        activo=True
    )
    db.session.add(prod)
    db.session.flush()
    
    # Movimiento inicial si stock > 0
    if stock > 0:
        mov = MovimientoInventario(
            id_producto=prod.id_producto,
            id_usuario=session.get('id_usuario'),
            tipo_movimiento='entrada',
            cantidad=stock,
            motivo='Registro inicial de producto nuevo en inventario'
        )
        db.session.add(mov)
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto creado exitosamente', 'producto': prod.to_dict()}), 201

@admin_bp.route('/productos/<int:id_producto>', methods=['PUT'])
@admin_required
def actualizar_producto(id_producto):
    prod = Producto.query.get(id_producto)
    if not prod:
        return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        
    data = request.get_json() or {}
    if 'nombre' in data:
        prod.nombre = data['nombre'].strip()
    if 'descripcion' in data:
        prod.descripcion = data['descripcion'].strip()
    if 'precio' in data:
        prod.precio = float(data['precio'])
    if 'id_categoria' in data:
        prod.id_categoria = int(data['id_categoria'])
    if 'imagen_url' in data:
        prod.imagen_url = data['imagen_url'].strip()
    if 'activo' in data:
        prod.activo = bool(data['activo'])
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Producto actualizado', 'producto': prod.to_dict()})

@admin_bp.route('/productos/<int:id_producto>', methods=['DELETE'])
@admin_required
def desactivar_producto(id_producto):
    prod = Producto.query.get(id_producto)
    if not prod:
        return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        
    prod.activo = False
    db.session.commit()
    return jsonify({'success': True, 'message': f'Producto "{prod.nombre}" desactivado del catálogo'})

# ==================== CATEGORÍAS ====================

@admin_bp.route('/categorias', methods=['POST'])
@admin_required
def crear_categoria():
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    
    if not nombre:
        return jsonify({'success': False, 'message': 'El nombre de la categoría es requerido'}), 400
        
    cat = Categoria(nombre=nombre, descripcion=descripcion, activo=True)
    db.session.add(cat)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Categoría creada', 'categoria': cat.to_dict()}), 201

# ==================== INVENTARIO Y MOVIMIENTOS ====================

@admin_bp.route('/inventario/movimiento', methods=['POST'])
@admin_required
def registrar_movimiento():
    data = request.get_json() or {}
    id_producto = data.get('id_producto')
    tipo = data.get('tipo_movimiento')  # 'entrada', 'salida', 'ajuste'
    cantidad = data.get('cantidad')
    motivo = data.get('motivo', '').strip()
    
    if not id_producto or not tipo or cantidad is None or not motivo:
        return jsonify({'success': False, 'message': 'Todos los campos del movimiento son requeridos'}), 400
        
    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            return jsonify({'success': False, 'message': 'La cantidad debe ser un entero positivo'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Cantidad numérica no válida'}), 400
        
    prod = Producto.query.get(id_producto)
    if not prod:
        return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        
    if tipo == 'entrada':
        prod.stock += cantidad
    elif tipo == 'salida':
        if prod.stock < cantidad:
            return jsonify({'success': False, 'message': f'Stock insuficiente. Stock actual: {prod.stock}'}), 400
        prod.stock -= cantidad
    elif tipo == 'ajuste':
        # En ajuste, la cantidad representa el nuevo valor real de stock
        diferencia = cantidad - prod.stock
        prod.stock = cantidad
        motivo = f"[Ajuste físico: {diferencia:+d}] {motivo}"
    else:
        return jsonify({'success': False, 'message': 'Tipo de movimiento inválido (entrada, salida, ajuste)'}), 400
        
    mov = MovimientoInventario(
        id_producto=prod.id_producto,
        id_usuario=session.get('id_usuario'),
        tipo_movimiento=tipo,
        cantidad=cantidad,
        motivo=motivo,
        fecha_movimiento=datetime.utcnow()
    )
    db.session.add(mov)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Movimiento de {tipo} registrado correctamente. Nuevo stock: {prod.stock}',
        'nuevo_stock': prod.stock
    })

@admin_bp.route('/inventario/movimientos', methods=['GET'])
@admin_required
def listar_movimientos():
    movimientos = MovimientoInventario.query.order_by(MovimientoInventario.fecha_movimiento.desc()).limit(100).all()
    return jsonify([m.to_dict() for m in movimientos])

# ==================== PEDIDOS Y ESTADOS ====================

@admin_bp.route('/pedidos', methods=['GET'])
@admin_required
def listar_pedidos():
    pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    return jsonify([p.to_dict() for p in pedidos])

@admin_bp.route('/pedidos/<int:id_pedido>/estado', methods=['PUT'])
@admin_required
def actualizar_estado_pedido(id_pedido):
    pedido = Pedido.query.get(id_pedido)
    if not pedido:
        return jsonify({'success': False, 'message': 'Pedido no encontrado'}), 404
        
    data = request.get_json() or {}
    nuevo_estado = data.get('estado')
    
    estados_validos = [
        'Pendiente de pago', 'Pagado', 'En preparación', 
        'Listo para entrega', 'Enviado', 'Entregado', 'Cancelado'
    ]
    
    if nuevo_estado not in estados_validos:
        return jsonify({'success': False, 'message': f'Estado no válido. Opciones: {", ".join(estados_validos)}'}), 400
        
    # Si se cancela un pedido que estaba pagado o pendiente, restaurar el inventario (RF-14, Sec 18.2)
    if nuevo_estado == 'Cancelado' and pedido.estado != 'Cancelado':
        for detalle in pedido.detalles:
            prod = Producto.query.get(detalle.id_producto)
            if prod:
                prod.stock += detalle.cantidad
                mov = MovimientoInventario(
                    id_producto=prod.id_producto,
                    id_usuario=session.get('id_usuario'),
                    tipo_movimiento='entrada',
                    cantidad=detalle.cantidad,
                    motivo=f'Devolución a inventario por cancelación de Pedido #{pedido.id_pedido}',
                    fecha_movimiento=datetime.utcnow()
                )
                db.session.add(mov)
                
    pedido.estado = nuevo_estado
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Estado del pedido #{pedido.id_pedido} actualizado a "{nuevo_estado}"',
        'pedido': pedido.to_dict()
    })

# ==================== REPORTES COMERCIALES ====================

@admin_bp.route('/reportes', methods=['GET'])
@admin_required
def obtener_reportes():
    # 1. Total ventas registradas
    total_ventas = db.session.query(func.coalesce(func.sum(Venta.total_venta), 0.0)).filter(Venta.estado == 'completada').scalar()
    
    # 2. Conteo de pedidos por estado
    estados_conteo = db.session.query(Pedido.estado, func.count(Pedido.id_pedido)).group_by(Pedido.estado).all()
    estados_dict = {estado: count for estado, count in estados_conteo}
    
    # 3. Productos más vendidos
    top_productos_query = db.session.query(
        Producto.nombre,
        func.sum(DetallePedido.cantidad).label('unidades_vendidas'),
        func.sum(DetallePedido.subtotal).label('total_recaudado')
    ).join(DetallePedido, Producto.id_producto == DetallePedido.id_producto)\
     .group_by(Producto.nombre)\
     .order_by(func.sum(DetallePedido.cantidad).desc())\
     .limit(5).all()
     
    top_productos = [
        {'nombre': row[0], 'unidades': int(row[1]), 'total': round(float(row[2]), 2)}
        for row in top_productos_query
    ]
    
    # 4. Alerta de productos con pocas existencias (<= 20 unidades)
    pocas_existencias = Producto.query.filter(Producto.activo == True, Producto.stock <= 20).order_by(Producto.stock.asc()).all()
    
    # 5. Métricas globales
    total_pedidos = Pedido.query.count()
    total_clientes = Usuario.query.filter_by(rol='cliente').count()
    total_articulos = Producto.query.filter_by(activo=True).count()
    
    return jsonify({
        'success': True,
        'metricas': {
            'total_ventas': round(float(total_ventas), 2),
            'total_pedidos': total_pedidos,
            'total_clientes': total_clientes,
            'total_articulos': total_articulos
        },
        'estados_pedidos': estados_dict,
        'top_productos': top_productos,
        'pocas_existencias': [p.to_dict() for p in pocas_existencias]
    })
