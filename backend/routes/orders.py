from flask import Blueprint, request, jsonify, session
from datetime import datetime
from backend.database import db
from backend.models import Usuario, Producto, Pedido, DetallePedido, MovimientoInventario, Pago, Venta

orders_bp = Blueprint('orders', __name__, url_prefix='/api/pedidos')

@orders_bp.route('/crear', methods=['POST'])
def crear_pedido():
    # 1. Verificar autenticación del cliente
    user_id = session.get('id_usuario')
    if not user_id:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para realizar un pedido'}), 401
        
    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.activo:
        return jsonify({'success': False, 'message': 'Usuario no válido'}), 403
        
    data = request.get_json() or {}
    items = data.get('items', [])
    direccion_entrega = data.get('direccion_entrega', '').strip()
    metodo_pago = data.get('metodo_pago', 'Pasarela Wompi Colombia')
    
    if not items:
        return jsonify({'success': False, 'message': 'El carrito no contiene productos'}), 400
        
    if not direccion_entrega:
        return jsonify({'success': False, 'message': 'La dirección de entrega es obligatoria'}), 400
        
    # 2. Validación en el backend de precios y stock (RF-09, RNF-06)
    total_calculado = 0.0
    detalles_a_crear = []
    productos_actualizar = []
    
    try:
        for item in items:
            prod_id = item.get('id_producto')
            cantidad = int(item.get('cantidad', 0))
            
            if cantidad <= 0:
                return jsonify({'success': False, 'message': 'Cantidad inválida para uno de los productos'}), 400
                
            producto = Producto.query.filter_by(id_producto=prod_id, activo=True).with_for_update().first()
            if not producto:
                return jsonify({'success': False, 'message': f'El producto con ID {prod_id} no está disponible'}), 404
                
            if producto.stock < cantidad:
                return jsonify({
                    'success': False, 
                    'message': f'Existencias insuficientes para "{producto.nombre}". Disponibles: {producto.stock}'
                }), 400
                
            precio_vigente = float(producto.precio)
            subtotal = precio_vigente * cantidad
            total_calculado += subtotal
            
            detalles_a_crear.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio_vigente,
                'subtotal': subtotal
            })
            
            # Decrementar stock atómicamente
            producto.stock -= cantidad
            productos_actualizar.append((producto, cantidad))
            
        # 3. Crear Pedido en base de datos
        nuevo_pedido = Pedido(
            id_usuario=usuario.id_usuario,
            fecha_pedido=datetime.utcnow(),
            total=total_calculado,
            estado='Pagado',  # Simulación aprobada de pasarela
            direccion_entrega=direccion_entrega
        )
        db.session.add(nuevo_pedido)
        db.session.flush()
        
        # 4. Crear DetallePedido y Movimientos de Inventario
        for det in detalles_a_crear:
            d = DetallePedido(
                id_pedido=nuevo_pedido.id_pedido,
                id_producto=det['producto'].id_producto,
                cantidad=det['cantidad'],
                precio_unitario=det['precio_unitario'],
                subtotal=det['subtotal']
            )
            db.session.add(d)
            
            # Trazabilidad de inventario: Salida por venta
            mov = MovimientoInventario(
                id_producto=det['producto'].id_producto,
                id_usuario=usuario.id_usuario,
                tipo_movimiento='salida',
                cantidad=det['cantidad'],
                motivo=f'Venta de confitería confirmada en Pedido #{nuevo_pedido.id_pedido}',
                fecha_movimiento=datetime.utcnow()
            )
            db.session.add(mov)
            
        # 5. Registrar Pago verificado (RF-16)
        nuevo_pago = Pago(
            id_pedido=nuevo_pedido.id_pedido,
            proveedor=metodo_pago,
            referencia_externa=f"PAY-{datetime.utcnow().strftime('%Y%m%d%H%M')}-{nuevo_pedido.id_pedido}",
            monto=total_calculado,
            estado='aprobado',
            fecha_pago=datetime.utcnow()
        )
        db.session.add(nuevo_pago)
        
        # 6. Registrar Venta completada (RF-17, RNF-06)
        nueva_venta = Venta(
            id_pedido=nuevo_pedido.id_pedido,
            fecha_venta=datetime.utcnow(),
            total_venta=total_calculado,
            estado='completada'
        )
        db.session.add(nueva_venta)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'¡Pedido #{nuevo_pedido.id_pedido} realizado exitosamente!',
            'pedido': nuevo_pedido.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al procesar la compra: {str(e)}'}), 500

@orders_bp.route('/mis-pedidos', methods=['GET'])
def get_mis_pedidos():
    user_id = session.get('id_usuario')
    if not user_id:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
        
    pedidos = Pedido.query.filter_by(id_usuario=user_id).order_by(Pedido.fecha_pedido.desc()).all()
    return jsonify({
        'success': True,
        'pedidos': [p.to_dict() for p in pedidos]
    })

@orders_bp.route('/<int:id_pedido>', methods=['GET'])
def get_pedido_detalle(id_pedido):
    user_id = session.get('id_usuario')
    if not user_id:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
        
    pedido = Pedido.query.get(id_pedido)
    if not pedido:
        return jsonify({'success': False, 'message': 'Pedido no encontrado'}), 404
        
    # Validar que pertenezca al usuario o sea admin
    rol = session.get('rol')
    if pedido.id_usuario != user_id and rol != 'administrador':
        return jsonify({'success': False, 'message': 'Acceso no autorizado a este pedido'}), 403
        
    return jsonify({
        'success': True,
        'pedido': pedido.to_dict()
    })
