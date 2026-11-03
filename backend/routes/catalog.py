from flask import Blueprint, request, jsonify
from backend.models import Producto, Categoria

catalog_bp = Blueprint('catalog', __name__, url_prefix='/api')

@catalog_bp.route('/categorias', methods=['GET'])
def get_categorias():
    categorias = Categoria.query.filter_by(activo=True).all()
    return jsonify([c.to_dict() for c in categorias])

@catalog_bp.route('/productos', methods=['GET'])
def get_productos():
    query = Producto.query.filter_by(activo=True)
    
    # Filtro por categoría
    categoria_id = request.args.get('categoria_id')
    if categoria_id and categoria_id.isdigit():
        query = query.filter_by(id_categoria=int(categoria_id))
        
    # Filtro de búsqueda por texto (nombre o descripción)
    search_q = request.args.get('q', '').strip()
    if search_q:
        query = query.filter(
            (Producto.nombre.ilike(f'%{search_q}%')) | 
            (Producto.descripcion.ilike(f'%{search_q}%'))
        )
        
    # Filtro por rango de precio
    min_price = request.args.get('min_price')
    if min_price:
        try:
            query = query.filter(Producto.precio >= float(min_price))
        except ValueError:
            pass
            
    max_price = request.args.get('max_price')
    if max_price:
        try:
            query = query.filter(Producto.precio <= float(max_price))
        except ValueError:
            pass
            
    # Filtro por disponibilidad
    in_stock = request.args.get('in_stock')
    if in_stock and in_stock.lower() in ['true', '1']:
        query = query.filter(Producto.stock > 0)
        
    productos = query.order_by(Producto.nombre.asc()).all()
    return jsonify([p.to_dict() for p in productos])

@catalog_bp.route('/productos/destacados', methods=['GET'])
def get_destacados():
    # Retorna los primeros 6 productos con stock
    destacados = Producto.query.filter_by(activo=True).filter(Producto.stock > 0).limit(6).all()
    return jsonify([p.to_dict() for p in destacados])

@catalog_bp.route('/productos/<int:id_producto>', methods=['GET'])
def get_producto_detalle(id_producto):
    producto = Producto.query.filter_by(id_producto=id_producto, activo=True).first()
    if not producto:
        return jsonify({'error': 'Producto no encontrado o inactivo'}), 404
        
    return jsonify(producto.to_dict())
