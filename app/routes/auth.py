from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from app.models.user import User
from app import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, redirigir al home
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(email=email).first()

        print(f"Email buscado: '{email}'")
        print(f"Usuario encontrado: {user}")
        if user:
            print(f"Password en BD: {user.password[:20]}...")  # solo los primeros 20 chars
            print(f"Hash válido: {check_password_hash(user.password, password)}")

        # Verificar existencia, contraseña y que la cuenta esté activa
        if not user or not check_password_hash(user.password, password):
            flash('Correo o contraseña incorrectos.', 'error')
            print("cuenta activada")
            return render_template('login.html')

        if not user.is_active:
            flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
            print("Cuenta desactivada")
            return render_template('login.html')

        # Login exitoso — actualizar last_login
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)

        # Redirigir a admin o usuario normal según rol
        if user.is_admin:
            print("redirigiendo")
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.home'))

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        name     = request.form.get('name', '').strip()

        # Validaciones básicas
        if not email or not password:
            flash('Correo y contraseña son obligatorios.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Ya existe una cuenta con ese correo.', 'error')
            return render_template('register.html')

        user = User(
            email=email,
            password=generate_password_hash(password),
            name=name,
            is_admin=False,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()

        flash('Cuenta creada correctamente. Inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))