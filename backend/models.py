from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='cliente', nullable=False)  # 'cliente' o 'administrador'
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    movimientos = db.relationship('MovimientoInventario', backref='usuario_responsable', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'correo': self.correo,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    productos = db.relationship('Producto', backref='categoria_rel', lazy=True)
    
    def to_dict(self):
        return {
            'id_categoria': self.id_categoria,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
            'total_productos': len(self.productos) if self.productos else 0
        }

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), nullable=False, index=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    imagen_url = db.Column(db.String(500), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    movimientos = db.relationship('MovimientoInventario', backref='producto', lazy=True, cascade="all, delete-orphan")
    detalles = db.relationship('DetallePedido', backref='producto_rel', lazy=True)
    
    def to_dict(self):
        return {
            'id_producto': self.id_producto,
            'id_categoria': self.id_categoria,
            'categoria': self.categoria_rel.nombre if self.categoria_rel else '',
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': round(float(self.precio), 2),
            'stock': self.stock,
            'imagen_url': self.imagen_url,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class MovimientoInventario(db.Model):
    __tablename__ = 'movimientos_inventario'
    
    id_movimiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False, index=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    tipo_movimiento = db.Column(db.String(20), nullable=False)  # 'entrada', 'salida', 'ajuste'
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    fecha_movimiento = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id_movimiento': self.id_movimiento,
            'id_producto': self.id_producto,
            'producto_nombre': self.producto.nombre if self.producto else 'Desconocido',
            'id_usuario': self.id_usuario,
            'usuario_nombre': self.usuario_responsable.nombre if self.usuario_responsable else 'Sistema',
            'tipo_movimiento': self.tipo_movimiento,
            'cantidad': self.cantidad,
            'motivo': self.motivo,
            'fecha_movimiento': self.fecha_movimiento.strftime('%Y-%m-%d %H:%M') if self.fecha_movimiento else None
        }

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False, index=True)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente de pago', nullable=False)
    # Estados permitidos: Pendiente de pago, Pagado, En preparación, Listo para entrega, Enviado, Entregado, Cancelado
    direccion_entrega = db.Column(db.String(255), nullable=True)
    
    detalles = db.relationship('DetallePedido', backref='pedido_rel', lazy=True, cascade="all, delete-orphan")
    pagos = db.relationship('Pago', backref='pedido_rel', lazy=True, cascade="all, delete-orphan")
    venta = db.relationship('Venta', backref='pedido_rel', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            'id_pedido': self.id_pedido,
            'id_usuario': self.id_usuario,
            'cliente_nombre': self.cliente.nombre if self.cliente else '',
            'cliente_correo': self.cliente.correo if self.cliente else '',
            'fecha_pedido': self.fecha_pedido.strftime('%Y-%m-%d %H:%M') if self.fecha_pedido else None,
            'total': round(float(self.total), 2),
            'estado': self.estado,
            'direccion_entrega': self.direccion_entrega,
            'detalles': [d.to_dict() for d in self.detalles] if self.detalles else [],
            'pagos': [p.to_dict() for p in self.pagos] if self.pagos else []
        }

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    
    id_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False, index=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id_detalle': self.id_detalle,
            'id_pedido': self.id_pedido,
            'id_producto': self.id_producto,
            'producto_nombre': self.producto_rel.nombre if self.producto_rel else 'Producto',
            'cantidad': self.cantidad,
            'precio_unitario': round(float(self.precio_unitario), 2),
            'subtotal': round(float(self.subtotal), 2)
        }

class Pago(db.Model):
    __tablename__ = 'pagos'
    
    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False, index=True)
    proveedor = db.Column(db.String(50), default='Wompi / Pasarela Virtual', nullable=False)
    referencia_externa = db.Column(db.String(100), nullable=True)
    monto = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(30), default='aprobado', nullable=False)  # 'pendiente', 'aprobado', 'rechazado', 'reembolsado'
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id_pago': self.id_pago,
            'id_pedido': self.id_pedido,
            'proveedor': self.proveedor,
            'referencia_externa': self.referencia_externa,
            'monto': round(float(self.monto), 2),
            'estado': self.estado,
            'fecha_pago': self.fecha_pago.strftime('%Y-%m-%d %H:%M') if self.fecha_pago else None
        }

class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), unique=True, nullable=False, index=True)
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_venta = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(30), default='completada', nullable=False)
    
    def to_dict(self):
        return {
            'id_venta': self.id_venta,
            'id_pedido': self.id_pedido,
            'fecha_venta': self.fecha_venta.strftime('%Y-%m-%d %H:%M') if self.fecha_venta else None,
            'total_venta': round(float(self.total_venta), 2),
            'estado': self.estado
        }
