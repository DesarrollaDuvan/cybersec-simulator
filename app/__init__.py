from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
load_dotenv()
from app.routes.chat import chat


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.register_blueprint(chat, url_prefix='/chat')

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app.models.user import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        db.create_all()  # crea las tablas si no existen

    # Blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.simulation import simulation
    # results.py ya NO se importa — la lógica vive en simulation.py
    from app.routes.quiz import quiz
    app.register_blueprint(quiz, url_prefix='/quiz')

    app.register_blueprint(main)
    app.register_blueprint(auth,       url_prefix='/auth')
    app.register_blueprint(simulation, url_prefix='/simulation')

    return app