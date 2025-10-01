from flask import Flask # type: ignore
from dotenv import load_dotenv # type: ignore
import os

def create_app():
    # Cargar variables de entorno desde el archivo .env
    load_dotenv()

    app = Flask(__name__)
   
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6')  # Usar variable de entorno o valor por defecto
    
    # Registrar rutas principales
    from .routes.routes import bp
    app.register_blueprint(bp)
    
    # Registrar rutas de analytics
    from .routes.analytics_routes import analytics_bp
    app.register_blueprint(analytics_bp)
    
    return app