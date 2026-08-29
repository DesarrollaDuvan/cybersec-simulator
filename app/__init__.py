from flask import Flask
from dotenv import load_dotenv

from app.extensions import db, login_manager, migrate, csrf, cache

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

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

    return app
