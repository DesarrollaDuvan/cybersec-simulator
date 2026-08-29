# tests/conftest.py
import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Crea una app Flask para testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de test para hacer requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner para comandos CLI."""
    return app.test_cli_runner()


@pytest.fixture
def authenticated_user(app, client):
    """Crea un usuario de test y lo loguea."""
    from app.models.user import User
    from werkzeug.security import generate_password_hash

    with app.app_context():
        user = User(
            email="test@example.com",
            password=generate_password_hash("testpass123"),
            name="Test User",
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Loguear al usuario
    client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "testpass123",
    }, follow_redirects=True)

    with app.app_context():
        user = db.session.get(User, user_id)

    return user