import unittest
import json
import os
import sys

# Asegurar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from backend.database import db
from backend.models import Usuario, Producto, Pedido, Categoria
from backend.services.gemini_service import responder_con_gemini

class CaramellTestCase(unittest.TestCase):
    def setUp(self):
        # Configurar base de datos de prueba en memoria
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # 1. PRUEBAS FUNCIONALES DE CATÁLOGO (RF-01, RF-02, RF-03, RF-04)
    def test_catalogo_productos_activos(self):
        response = self.client.get('/api/productos')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)
        self.assertTrue(all(p['activo'] for p in data))

    def test_busqueda_productos(self):
        response = self.client.get('/api/productos?q=chocolate')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(any('chocolate' in p['nombre'].lower() for p in data))

    def test_filtro_categoria(self):
        response = self.client.get('/api/productos?categoria_id=1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(all(p['id_categoria'] == 1 for p in data))

    # 2. PRUEBAS DE AUTENTICACIÓN Y SEGURIDAD (RF-06, RF-07, RNF-04)
    def test_registro_usuario(self):
        response = self.client.post('/api/auth/register', json={
            'nombre': 'Estudiante Demo',
            'correo': 'estudiante@test.com',
            'password': 'Password123*'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['usuario']['correo'], 'estudiante@test.com')
        self.assertEqual(data['usuario']['rol'], 'cliente')

    def test_registro_administrador_exitoso(self):
        response = self.client.post('/api/auth/register', json={
            'nombre': 'Nuevo Dueno Tienda',
            'correo': 'dueno@test.com',
            'password': 'DuenoPassword123*',
            'rol': 'administrador',
            'codigo_admin': 'CARAMELL-PROPIETARIO-2026'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['usuario']['rol'], 'administrador')
        self.assertEqual(data['redirect'], '/admin')

    def test_registro_administrador_codigo_invalido(self):
        response = self.client.post('/api/auth/register', json={
            'nombre': 'Hacker Admin',
            'correo': 'hacker@test.com',
            'password': 'Password123*',
            'rol': 'administrador',
            'codigo_admin': 'CLAVE-FALSA-999'
        })
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_login_cliente_en_portal_admin_rechazado(self):
        response = self.client.post('/api/auth/login', json={
            'correo': 'camilo.perez@caramellmomen.com',
            'password': 'Cliente123*',
            'portal_tipo': 'administrador'
        })
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_login_correcto(self):
        response = self.client.post('/api/auth/login', json={
            'correo': 'admin@caramellmomen.com',
            'password': 'Admin123*'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['usuario']['rol'], 'administrador')

    def test_login_invalido(self):
        response = self.client.post('/api/auth/login', json={
            'correo': 'admin@caramellmomen.com',
            'password': 'ClaveIncorrecta'
        })
        self.assertEqual(response.status_code, 401)

    # 3. PRUEBAS DE PEDIDOS Y CONTROL DE INVENTARIO (RF-09, RF-10, RF-14)
    def test_creacion_pedido_con_descuento_stock(self):
        # Iniciar sesión como cliente
        self.client.post('/api/auth/login', json={
            'correo': 'camilo.perez@caramellmomen.com',
            'password': 'Cliente123*'
        })

        with self.app.app_context():
            prod = Producto.query.first()
            prod_id = prod.id_producto
            stock_inicial = prod.stock

        # Realizar compra
        response = self.client.post('/api/pedidos/crear', json={
            'items': [{'id_producto': prod_id, 'cantidad': 2}],
            'direccion_entrega': 'Calle 100 # 15-20, Bogotá',
            'metodo_pago': 'Wompi Oficial'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

        # Verificar que el stock se redujo exactamente en 2 unidades
        with self.app.app_context():
            prod_actualizado = Producto.query.get(prod_id)
            self.assertEqual(prod_actualizado.stock, stock_inicial - 2)

    def test_rechazo_stock_insuficiente(self):
        self.client.post('/api/auth/login', json={
            'correo': 'camilo.perez@caramellmomen.com',
            'password': 'Cliente123*'
        })
        with self.app.app_context():
            prod = Producto.query.first()
            prod_id = prod.id_producto

        response = self.client.post('/api/pedidos/crear', json={
            'items': [{'id_producto': prod_id, 'cantidad': 99999}],
            'direccion_entrega': 'Dirección Demo'
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    # 4. PRUEBAS DEL ASISTENTE VIRTUAL CARAMELL ASSISTANT (RF-18, Sec 23, 24, 25)
    def test_chatbot_derivacion_humana_cobro_duplicado(self):
        with self.app.app_context():
            res = responder_con_gemini("Me cobraron dos veces el mismo pedido")
            self.assertTrue(res['derivacion_humana'])
            self.assertIn("contacto@caramellmomen.com", res['respuesta'])
            self.assertIn("nunca", res['respuesta'].lower())

    def test_chatbot_fuera_de_alcance(self):
        with self.app.app_context():
            res = responder_con_gemini("Hazme una tarea de programacion en python")
            self.assertFalse(res['derivacion_humana'])
            self.assertIn("CARAMELL MOMEN S.A.S.", res['respuesta'])
            self.assertIn("exclusivamente", res['respuesta'].lower())

    def test_chatbot_consulta_producto(self):
        with self.app.app_context():
            res = responder_con_gemini("¿Qué chocolates tienen?")
            self.assertIn("Chocolate", res['respuesta'])

    # 5. SEGURIDAD: ACCESO PROTEGIDO A PANEL ADMINISTRATIVO
    def test_seguridad_admin_rechaza_cliente(self):
        # Iniciar sesión como cliente
        self.client.post('/api/auth/login', json={
            'correo': 'camilo.perez@caramellmomen.com',
            'password': 'Cliente123*'
        })
        # Intentar crear producto
        response = self.client.post('/api/admin/productos', json={
            'nombre': 'Dulce Hacker',
            'id_categoria': 1,
            'precio': 1000
        })
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
