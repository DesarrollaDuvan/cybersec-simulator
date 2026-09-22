import os

from flask import Config, Flask, send_from_directory
from dotenv import load_dotenv

from app.extensions import db, login_manager, migrate, csrf, cache

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Establece la ruta de instancia escribible en Vercel
    if os.getenv("VERCEL") == "1":  # Detecta ambiente Vercel si es necesario
        app.instance_path = '/tmp/instance'

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        # Maneja posibles errores de permisos si /tmp no existe o no es escribible
        pass

    app.config.from_object(Config)


    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    

    with app.app_context():
        from app.models.user import User
        from app.models.progress import SimulationProgress  # noqa: F401

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        db.create_all()

    # Blueprints
    from app.routes.chat import chat
    from app.routes.admin import admin
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.simulation import simulation
    from app.routes.simulation_immersive import sim_immersive
    from app.routes.quiz import quiz

    app.register_blueprint(chat, url_prefix='/chat')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(simulation, url_prefix='/simulation')
    app.register_blueprint(sim_immersive, url_prefix='/sim')
    app.register_blueprint(quiz, url_prefix='/quiz')

    # Servir archivos estáticos en producción (Vercel)
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)

    return app
