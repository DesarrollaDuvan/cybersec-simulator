from flask import Blueprint, render_template, request, redirect, url_for
from app.core.simulator import phishing_scenario


simulation = Blueprint('simulation', __name__)

def phishing_scenario(action):

    if action == "open_email":
        return {
            "result": "fail",
            "message": "Caíste en phishing"
        }

    return {
        "result": "success",
        "message": "Detectaste el ataque"
    }

@simulation.route('/')
def start():
    return render_template('simulation.html')


@simulation.route('/decision', methods=['POST'])
def decision():
    user_action = request.form.get('action')

    if user_action == "open_email":
        result = "phishing_fail"
    else:
        result = "safe"

    return redirect(url_for('results.show_result', result=result))

