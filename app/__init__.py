from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()   # 👈 inicializas sin pasar app todavía

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)   # 👈 aquí sí pasas app y db

    with app.app_context():
        from app.models.user import User

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
    from app.routes.quiz import quiz

    app.register_blueprint(chat, url_prefix='/chat')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(simulation, url_prefix='/simulation')
    app.register_blueprint(quiz, url_prefix='/quiz')

    return app
