import os


from flask import Flask, jsonify
from flask_swagger import swagger

# Identifica el directorio base
basedir = os.path.abspath(os.path.dirname(__file__))

def registrar_handlers():
    import modulos.eventos.aplicacion


def importar_modelos_alchemy():
    import modulos.eventos.infraestructura.dto
    import eventosMS.modulos.sagas.infraestructura.modelos 


def comenzar_consumidor(app):
    import threading
    import modulos.eventos.infraestructura.consumidores as eventos
    import modulos.sagas.infraestructura.consumidores as sagas

    def run_with_context(target, *args):
        with app.app_context():
            target(*args)

    threading.Thread(target=run_with_context, args=(eventos.suscribirse_a_eventos_pago, app)).start()
    threading.Thread(target=run_with_context, args=(eventos.suscribirse_a_comandos_evento, app)).start()
    threading.Thread(target=run_with_context, args=(sagas.subscribirse_a_eventos_bff, app)).start()
    threading.Thread(target=run_with_context, args=(sagas.subscribirse_a_eventos_tracking, app)).start()
    threading.Thread(target=run_with_context, args=(sagas.subscribirse_a_evento_referido, app)).start()
    threading.Thread(target=run_with_context, args=(sagas.subscribirse_a_eventos_pago, app)).start()




def create_app(configuracion={}):
    # Init la aplicacion de Flask
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure PostgreSQL database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5435')
    DB_NAME = os.environ.get('DB_NAME', 'alpespartners')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres123')
    
    # Use SQLite for testing, PostgreSQL for production
    if configuracion.get('TESTING'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    else:
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
            comenzar_consumidor(app)

     # Importa Blueprints
    from . import eventos


    # Registro de Blueprints
    app.register_blueprint(eventos.bp)


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
