# seed.py — ejecutar UNA sola vez: python seed.py

from werkzeug.security import generate_password_hash
from datetime import datetime
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Limpiar usuarios existentes (opcional)
    User.query.delete()

    admin = User(
        email='duvan3828@gmail.com',
        password=generate_password_hash('Admin1234'),
        name='Administrador',
        is_admin=True,
        is_active=True,
        created_at=datetime.utcnow()
    )

    cliente = User(
        email='leonela@gmail.com',
        password=generate_password_hash('Cliente1234'),
        name='Usuario Demo',
        is_admin=False,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.session.add_all([admin, cliente])
    db.session.commit()

    print("✅ Usuarios creados:")
    print(f"   Admin:   admin@cybertutor.com   / Admin123!")
    print(f"   Cliente: cliente@cybertutor.com / Cliente123!")