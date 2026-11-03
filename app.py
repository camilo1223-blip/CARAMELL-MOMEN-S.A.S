import os
import sys
from flask import Flask, render_template, send_from_directory, redirect, url_for, session

# Asegurar path y codificación UTF-8 en consola Windows
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.config import Config
from backend.database import db
from backend.models import Producto, Categoria, Usuario, Pedido
from backend.seed_data import seed_database

from backend.routes.auth import auth_bp
from backend.routes.catalog import catalog_bp
from backend.routes.orders import orders_bp
from backend.routes.admin import admin_bp
from backend.routes.chatbot import chatbot_bp

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'static')
    )
    
    app.config.from_object(Config)
    
    # Inicializar Base de Datos
    db.init_app(app)
    
    # Registrar Blueprints API
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)
    
    # Rutas Web Frontend
    @app.route('/')
    def index():
        return render_template('index.html')
        
    @app.route('/catalogo')
    def catalogo():
        return render_template('catalogo.html')
        
    @app.route('/producto/<int:id_producto>')
    def producto_detalle(id_producto):
        return render_template('producto.html', id_producto=id_producto)
        
    @app.route('/carrito')
    def carrito():
        return render_template('carrito.html')
        
    @app.route('/pedidos')
    def pedidos():
        return render_template('pedidos.html')
        
    @app.route('/login')
    def login_view():
        return render_template('login.html')
        
    @app.route('/registro')
    def registro_view():
        return render_template('registro.html')
        
    @app.route('/admin')
    def admin_view():
        # Verificación básica en vista
        if session.get('rol') != 'administrador':
            return redirect(url_for('login_view'))
        return render_template('admin.html')
        
    with app.app_context():
        db.create_all()
        seed_database()
        
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"===============================================================")
    print(f"[CARAMELL] CARAMELL MOMEN S.A.S. - Servidor Web Iniciado en puerto {port}")
    print(f"[CARAMELL] Accede en tu navegador a: http://127.0.0.1:{port}")
    print(f"===============================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
