from flask import Flask # type: ignore

def create_app():
    app = Flask(__name__)
    # Configuraciones adicionales (si las necesitas)
    app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'  # Cambia esto por una clave segura
    
    # Registrar rutas
    from .routes.routes import bp
    app.register_blueprint(bp)
    
    return app
