import os

from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_swagger import swagger

# Identifica el directorio base
basedir = os.path.abspath(os.path.dirname(__file__))

def registrar_handlers():
    import modulos.referidos.aplicacion


def importar_modelos_alchemy():
    import modulos.referidos.infraestructura.dto


def comenzar_consumidor():
    """
    Este es un código de ejemplo. Aunque esto sea funcional puede ser un poco peligroso tener 
    threads corriendo por si solos. Mi sugerencia es en estos casos usar un verdadero manejador
    de procesos y threads como Celery.
    """

    import threading
    import modulos.referidos.infraestructura.consumidores as referidos
    from flask import current_app

    # Obtener el contexto de aplicación actual
    app = current_app._get_current_object()

    # Función wrapper para ejecutar con contexto de aplicación
    def run_with_app_context(target_func):
        def wrapper():
            with app.app_context():
                target_func()
        return wrapper

    # Suscripción a eventos principales según especificación
    threading.Thread(target=run_with_app_context(referidos.suscribirse_a_eventos_tracking)).start()
    
    # Suscripciones legacy para compatibilidad
    threading.Thread(target=run_with_app_context(referidos.suscribirse_a_comandos_eventos)).start()
    threading.Thread(target=run_with_app_context(referidos.suscribirse_a_comandos_referidos)).start()

def create_app(configuracion={}):
    # Init la aplicacion de Flask
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'alpespartners')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    AMBIENTE = os.environ.get('AMBIENTE', 'produccion')
    
    # Use SQLite only for testing, PostgreSQL for development and production
    if configuracion.get('TESTING'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    else:
        # Use PostgreSQL for both development and production
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        else:
            # Fallback to individual environment variables
            app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.secret_key = '9d58f98f-3ae8-4149-a09f-3a8c2012e32c'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['TESTING'] = configuracion.get('TESTING')

     # Inicializa la DB
    from config.db import init_db, db
    
    init_db(app)
    importar_modelos_alchemy()
    registrar_handlers()

    with app.app_context():
        db.create_all()
        if not app.config.get('TESTING'):
            comenzar_consumidor()

     # Importa Blueprints
    from . import referidos


    # Registro de Blueprints
    app.register_blueprint(referidos.bp)


    @app.route("/spec")
    def spec():
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "My API"
        return jsonify(swag)

    @app.route("/health")
    def health():
        return {"status": "up"}
    

    return app
