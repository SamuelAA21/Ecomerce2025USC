from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Definir clave secreta después de crear app
    app.secret_key = 'ECOMERCE2025'

    # Importar y registrar las rutas
    from .routes import main
    app.register_blueprint(main)

    return app
