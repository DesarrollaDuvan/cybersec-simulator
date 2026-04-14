from flask import Blueprint, render_template, request, redirect, url_for
from app.models.user import User
from flask_login import login_user
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('main.home'))
        
        else:
            return "Credenciales incorrectas"

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User(email=email, password=password)

        db.session.add(user)
        db.session.commit()

        return redirect('/auth/login')

    return render_template('register.html')