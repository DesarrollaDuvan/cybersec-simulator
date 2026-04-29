from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    return render_template('dashboard.html')

@main.route('/phishing')
def phishing():
    return render_template('phishing.html')

@main.route('/contraseña')
def contraseña():
    return render_template('contraseña.html')

@main.route('/ingenieria')
def ingenieria():
    return render_template('ingenieria.html')

@main.route('/redes')
def redes():
    return render_template('redes.html')

@main.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html', stage='start')

@main.route('/quiz/play')
@login_required
def play_quiz():
    return render_template('quiz_play.html') 