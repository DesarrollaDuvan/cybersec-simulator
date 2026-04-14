from flask import Blueprint, render_template

results = Blueprint('results', __name__)

@results.route('/<result>')
def show_result(result):

    if result == "phishing_fail":
        message = "⚠️ Caíste en phishing"
        risk = "Alto"
    else:
        message = "✅ Decisión segura"
        risk = "Bajo"

    return render_template('result.html', message=message, risk=risk)