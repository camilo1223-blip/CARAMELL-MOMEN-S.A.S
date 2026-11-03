from datetime import datetime, timedelta
from backend.database import db
from backend.models import Usuario, Categoria, Producto, MovimientoInventario, Pedido, DetallePedido, Pago, Venta

def seed_database():
    """Inicializa la base de datos con categorías, productos, usuarios y datos demo."""
    if Usuario.query.first():
        # Ya existen datos cargados
        return

    print("Cargando datos iniciales de CARAMELL MOMEN S.A.S....")

    # 1. Crear Usuarios iniciales
    admin = Usuario(
        nombre="Administrador Caramell",
        correo="admin@caramellmomen.com",
        rol="administrador",
        activo=True
    )
    admin.set_password("Admin123*")

    cliente = Usuario(
        nombre="Camilo Andrés Pérez Padilla",
        correo="camilo.perez@caramellmomen.com",
        rol="cliente",
        activo=True
    )
    cliente.set_password("Cliente123*")

    db.session.add_all([admin, cliente])
    db.session.flush()

    # 2. Crear Categorías
    categorias_data = [
        {"nombre": "Chocolates", "descripcion": "Exquisitos chocolates artesanales, barras de cacao fino y tabletas rellenas."},
        {"nombre": "Caramelos", "descripcion": "Caramelos masticables, duros, ácidos y con centros cremosos frutales."},
        {"nombre": "Gomitas", "descripcion": "Gomitas suaves y azucaradas con divertidas formas de ositos, aros y frutas."},
        {"nombre": "Chupetas", "descripcion": "Paletas de caramelo macizo y rellenas de chicle con sabores intensos."},
        {"nombre": "Bombones", "descripcion": "Finos bombones rellenos de arequipe, licor, avellanas y trufa de chocolate."},
        {"nombre": "Paquetes de Dulces", "descripcion": "Surtidos festivos y anchetas temáticas ideales para fiestas y piñatas."}
    ]

    cat_map = {}
    for c_data in categorias_data:
        cat = Categoria(
            nombre=c_data["nombre"],
            descripcion=c_data["descripcion"],
            activo=True
        )
        db.session.add(cat)
        db.session.flush()
        cat_map[c_data["nombre"]] = cat.id_categoria

    # 3. Crear Productos de Confitería
    productos_data = [
        # Chocolates
        {
            "id_categoria": cat_map["Chocolates"],
            "nombre": "Barra Chocolate Suizo 70% Cacao",
            "descripcion": "Chocolate negro puro de origen alpino con toques sutiles de vainilla y aroma tostado. Barra de 100g.",
            "precio": 9500.0,
            "stock": 45,
            "imagen_url": "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Chocolates"],
            "nombre": "Chocolatina de Leche con Almendras",
            "descripcion": "Cremoso chocolate con leche enriquecido con crujientes almendras enteras tostadas al horno.",
            "precio": 5200.0,
            "stock": 60,
            "imagen_url": "https://images.unsplash.com/photo-1548907040-4baa42d10919?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Chocolates"],
            "nombre": "Monedas de Chocolate Dorado",
            "descripcion": "Bolsa de 20 monedas de chocolate con leche envueltas en papel dorado brillante.",
            "precio": 6800.0,
            "stock": 35,
            "imagen_url": "https://images.unsplash.com/photo-1511381939415-e44015466834?w=600&auto=format&fit=crop&q=80"
        },
        # Caramelos
        {
            "id_categoria": cat_map["Caramelos"],
            "nombre": "Caramelos Masticables Menta Glacial",
            "descripcion": "Caramelos refrescantes de menta natural con textura suave y centro líquido helado. Paquete x 50 uds.",
            "precio": 4500.0,
            "stock": 70,
            "imagen_url": "https://images.unsplash.com/photo-1582058091505-f87a2e55a40f?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Caramelos"],
            "nombre": "Caramelos Ácidos Frutos Rojos",
            "descripcion": "Caramelos duros con cubierta súper ácida que explota en sabor dulce a fresa, mora y arándano.",
            "precio": 3800.0,
            "stock": 50,
            "imagen_url": "https://images.unsplash.com/photo-1575224300306-1b8da36134ec?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Caramelos"],
            "nombre": "Caramelos de Mantequilla Toffee Artesanal",
            "descripcion": "Clásicos toffees ingleses cocidos a fuego lento con mantequilla de campo y crema de leche.",
            "precio": 7500.0,
            "stock": 30,
            "imagen_url": "https://images.unsplash.com/photo-1526081347589-7fa3cb41b4b2?w=600&auto=format&fit=crop&q=80"
        },
        # Gomitas
        {
            "id_categoria": cat_map["Gomitas"],
            "nombre": "Ositos de Goma Multifruta Clásicos",
            "descripcion": "Bolsa de gomitas suaves en 5 deliciosos sabores: manzana verde, naranja, piña, frambuesa y limón. 250g.",
            "precio": 4200.0,
            "stock": 80,
            "imagen_url": "https://images.unsplash.com/photo-1582058091505-f87a2e55a40f?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Gomitas"],
            "nombre": "Aros de Gomita Melocotón Neón",
            "descripcion": "Aros bicolores espolvoreados con azúcar cristalizado y un irresistible aroma a durazno maduro.",
            "precio": 4600.0,
            "stock": 40,
            "imagen_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Gomitas"],
            "nombre": "Gusanitos Ácidos Tropicales",
            "descripcion": "Gomitas alargadas con doble sabor y cobertura efervescente ácida de maracuyá y mango.",
            "precio": 3900.0,
            "stock": 65,
            "imagen_url": "https://images.unsplash.com/photo-1581798459219-318e76aecc7b?w=600&auto=format&fit=crop&q=80"
        },
        # Chupetas
        {
            "id_categoria": cat_map["Chupetas"],
            "nombre": "Chupeta Gigante Rellena de Chicle Cereza",
            "descripcion": "Paleta de caramelo cristalino sabor cereza roja con corazón de goma de mascar inflable. Display x 24 uds.",
            "precio": 14500.0,
            "stock": 25,
            "imagen_url": "https://images.unsplash.com/photo-1575224300306-1b8da36134ec?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Chupetas"],
            "nombre": "Paletas Arcoíris Espiraladas",
            "descripcion": "Tradicionales piruletas circulares artesanales con vistosos colores festivos y sabor tutti frutti.",
            "precio": 6000.0,
            "stock": 35,
            "imagen_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=80"
        },
        # Bombones
        {
            "id_categoria": cat_map["Bombones"],
            "nombre": "Caja de Bombones Surtidos Selección Oro",
            "descripcion": "Elegante caja de regalo con 12 bombones rellenos de praliné de avellana, café moka y crema de pistacho.",
            "precio": 24000.0,
            "stock": 20,
            "imagen_url": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Bombones"],
            "nombre": "Trufas Francesas de Chocolate Amargo",
            "descripcion": "Delicadas trufas espolvoreadas con fino cacao holandés de textura que se funde en el paladar.",
            "precio": 18500.0,
            "stock": 18,
            "imagen_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=600&auto=format&fit=crop&q=80"
        },
        # Paquetes de Dulces
        {
            "id_categoria": cat_map["Paquetes de Dulces"],
            "nombre": "Mega Pack Fiesta Piñata 1.5 Kg",
            "descripcion": "Surtido masivo con más de 120 unidades de golosinas variadas: chocolates, chupetas, gomitas y caramelos.",
            "precio": 32000.0,
            "stock": 15,
            "imagen_url": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id_categoria": cat_map["Paquetes de Dulces"],
            "nombre": "Combo Dulce Momento Parejas",
            "descripcion": "Ancheta decorativa con ositos de goma, dos barras suizas, bombones de avellana y tarjeta de felicitación.",
            "precio": 38000.0,
            "stock": 12,
            "imagen_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80"
        }
    ]

    prod_objs = []
    for p_info in productos_data:
        prod = Producto(
            id_categoria=p_info["id_categoria"],
            nombre=p_info["nombre"],
            descripcion=p_info["descripcion"],
            precio=p_info["precio"],
            stock=p_info["stock"],
            imagen_url=p_info["imagen_url"],
            activo=True
        )
        db.session.add(prod)
        db.session.flush()
        prod_objs.append(prod)

        # Registrar movimiento inicial de inventario
        mov = MovimientoInventario(
            id_producto=prod.id_producto,
            id_usuario=admin.id_usuario,
            tipo_movimiento="entrada",
            cantidad=prod.stock,
            motivo="Carga inicial de inventario de apertura de tienda"
        )
        db.session.add(mov)

    # 4. Crear un pedido de ejemplo completado para Camilo
    pedido_demo = Pedido(
        id_usuario=cliente.id_usuario,
        fecha_pedido=datetime.utcnow() - timedelta(days=2),
        total=33500.0,
        estado="Pagado",
        direccion_entrega="Calle 72 # 45-20, Apto 502, Barranquilla, Colombia"
    )
    db.session.add(pedido_demo)
    db.session.flush()

    # Detalles del pedido demo
    det1 = DetallePedido(
        id_pedido=pedido_demo.id_pedido,
        id_producto=prod_objs[0].id_producto,
        cantidad=2,
        precio_unitario=prod_objs[0].precio,
        subtotal=prod_objs[0].precio * 2
    )
    det2 = DetallePedido(
        id_pedido=pedido_demo.id_pedido,
        id_producto=prod_objs[9].id_producto,
        cantidad=1,
        precio_unitario=prod_objs[9].precio,
        subtotal=prod_objs[9].precio
    )
    db.session.add_all([det1, det2])

    pago_demo = Pago(
        id_pedido=pedido_demo.id_pedido,
        proveedor="Wompi Pasarela Oficial",
        referencia_externa="WMP-20261024-99881",
        monto=33500.0,
        estado="aprobado",
        fecha_pago=datetime.utcnow() - timedelta(days=2)
    )
    db.session.add(pago_demo)

    venta_demo = Venta(
        id_pedido=pedido_demo.id_pedido,
        fecha_venta=datetime.utcnow() - timedelta(days=2),
        total_venta=33500.0,
        estado="completada"
    )
    db.session.add(venta_demo)

    # 5. Crear un segundo pedido en preparación
    pedido_demo2 = Pedido(
        id_usuario=cliente.id_usuario,
        fecha_pedido=datetime.utcnow() - timedelta(hours=4),
        total=24000.0,
        estado="En preparación",
        direccion_entrega="Calle 72 # 45-20, Apto 502, Barranquilla, Colombia"
    )
    db.session.add(pedido_demo2)
    db.session.flush()

    det3 = DetallePedido(
        id_pedido=pedido_demo2.id_pedido,
        id_producto=prod_objs[11].id_producto,  # Caja bombones
        cantidad=1,
        precio_unitario=prod_objs[11].precio,
        subtotal=prod_objs[11].precio
    )
    db.session.add(det3)

    pago_demo2 = Pago(
        id_pedido=pedido_demo2.id_pedido,
        proveedor="Mercado Pago Colombia",
        referencia_externa="MP-77441122-COL",
        monto=24000.0,
        estado="aprobado",
        fecha_pago=datetime.utcnow() - timedelta(hours=4)
    )
    db.session.add(pago_demo2)

    venta_demo2 = Venta(
        id_pedido=pedido_demo2.id_pedido,
        fecha_venta=datetime.utcnow() - timedelta(hours=4),
        total_venta=24000.0,
        estado="completada"
    )
    db.session.add(venta_demo2)

    db.session.commit()
    print("Base de datos inicializada con éxito con usuarios, categorías, catálogo y pedidos.")
