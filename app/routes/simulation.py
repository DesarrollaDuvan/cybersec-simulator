import os
import json
import random
from flask import Blueprint, render_template, request, session
from flask_login import login_required
from anthropic import Anthropic

simulation = Blueprint("simulation", __name__)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


from app.models.progress import QuizResult, SimulationResult
from app import db
from flask_login import current_user

# ---------------------------------------------------------------------------
# ESCENARIOS DE PHISHING (puedes mover esto a una BD o JSON externo)
# ---------------------------------------------------------------------------

SCENARIOS = [
    {
        "id": "sc_001",
        "sender": "soporte@banco-seguro-col.net",
        "subject": "⚠ Urgente: Su cuenta ha sido bloqueada",
        "body": (
            "Estimado cliente, hemos detectado actividad sospechosa en su cuenta. "
            "Para evitar el bloqueo permanente, debe verificar su identidad en las "
            "próximas 24 horas. Haga clic en el enlace para actualizar sus datos."
        ),
        "link": "http://banco-seguro-col.net/verificar?token=abc123",
        "correct_action": "report",
        "risk": "alto",
        "clues": [
            "El dominio no coincide con el banco real (.net en lugar de .com.co)",
            "Lenguaje de urgencia: '24 horas', 'bloqueo permanente'",
            "Enlace con parámetros sospechosos en la URL",
            "Solicita información personal por correo",
        ],
    },
    {
        "id": "sc_002",
        "sender": "rrhh@miempresa.com",
        "subject": "Actualización de datos para nómina — Plazo: viernes",
        "body": (
            "Hola equipo, como parte de la actualización del sistema de nómina, "
            "necesitamos que confirmes tu número de cuenta bancaria y cédula en el "
            "formulario adjunto. Por favor hazlo antes del viernes."
        ),
        "link": None,
        "correct_action": "ignore",
        "risk": "medio",
        "clues": [
            "Solicita datos bancarios por correo, algo que RRHH nunca haría",
            "Sin firma ni datos de contacto del remitente",
            "Presión de tiempo ('antes del viernes')",
            "Dominio parece correcto, pero el contenido es sospechoso",
        ],
    },
    {
        "id": "sc_003",
        "sender": "no-reply@netflix.com",
        "subject": "Tu suscripción expira hoy — Actualiza tu método de pago",
        "body": (
            "Tu suscripción a Netflix está a punto de expirar. Para seguir disfrutando "
            "de tu contenido favorito sin interrupciones, actualiza tu método de pago "
            "ahora. Si no lo haces, tu cuenta será cancelada esta noche."
        ),
        "link": "http://netflix-pagos.com/update",
        "correct_action": "report",
        "risk": "alto",
        "clues": [
            "El enlace lleva a un dominio falso: 'netflix-pagos.com' no es de Netflix",
            "Netflix nunca envía correos con amenazas de cancelación inmediata",
            "Urgencia artificial: 'esta noche'",
            "El remitente parece legítimo pero la URL revela el fraude",
        ],
    },
]


def get_scenario(scenario_id=None):
    """Retorna un escenario por ID, o uno aleatorio si no se especifica."""
    if scenario_id:
        return next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    return random.choice(SCENARIOS)


# ---------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL: ANÁLISIS CON CLAUDE
# ---------------------------------------------------------------------------

def analyze_decision_with_claude(scenario: dict, user_action: str) -> dict:
    """
    Llama a la API de Claude para analizar la decisión del usuario
    y generar un análisis educativo personalizado.

    Retorna un dict con:
      - analysis: explicación detallada de Claude
      - tip: consejo para el futuro
      - points: puntuación (0-100)
    """

    action_labels = {
        "click_link": "Abrió el enlace sospechoso",
        "reply": "Respondió el correo con información",
        "ignore": "Ignoró y eliminó el correo",
        "report": "Reportó el correo como phishing",
    }

    prompt = f"""
Eres CyberTutor IA, un experto en ciberseguridad que enseña a identificar ataques de phishing.
Un usuario acaba de enfrentar el siguiente escenario de simulación:

ESCENARIO:
- Remitente: {scenario['sender']}
- Asunto: {scenario['subject']}
- Cuerpo del correo: {scenario['body']}
- Enlace incluido: {scenario.get('link', 'Ninguno')}
- Señales de alerta reales: {', '.join(scenario['clues'])}
- Acción correcta: {scenario['correct_action']}

DECISIÓN DEL USUARIO: {action_labels.get(user_action, user_action)}

Responde ÚNICAMENTE con un objeto JSON con esta estructura exacta (sin markdown, sin texto extra):
{{
  "analysis": "Explicación clara de 3-4 oraciones sobre por qué la decisión fue correcta o incorrecta, mencionando las señales concretas del correo.",
  "tip": "Un consejo práctico de 1-2 oraciones para situaciones similares en el futuro.",
  "points": <número entre 0 y 100 según la calidad de la decisión>
}}

Reglas para los puntos:
- report (correcto): 100
- ignore (aceptable): 75
- reply (mala): 25
- click_link (peligroso): 0
Si la acción correcta era 'ignore' y el usuario reportó, dale 90 puntos (casi perfecto).
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Limpiar posibles backticks de markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)
    return result


# ---------------------------------------------------------------------------
# RUTAS DEL BLUEPRINT
# ---------------------------------------------------------------------------

@simulation.route("/")
def start_simulation():
    """Muestra un escenario de phishing al usuario."""
    scenario = get_scenario()
    session["current_scenario"] = scenario["id"]
    return render_template("simulation.html", scenario=scenario)


@simulation.route("/decision", methods=["POST"])
@login_required
def simulation_decision():
    """Procesa la decisión del usuario y consulta a Claude para el análisis."""

    user_action = request.form.get("action")
    scenario_id = request.form.get("scenario_id") or session.get("current_scenario")

    scenario = get_scenario(scenario_id)
    if not scenario:
        return "Escenario no encontrado", 404

    # Llamada a Claude
    try:
        ai_result = analyze_decision_with_claude(scenario, user_action)
    except Exception as e:
        # Fallback si hay error con la API
        ai_result = {
            "analysis": "No se pudo conectar con CyberTutor IA en este momento. Revisa tu API key.",
            "tip": "Siempre verifica el dominio del remitente antes de hacer clic en cualquier enlace.",
            "points": 0,
        }

    # Determinar nivel de riesgo según la acción
    risk_map = {"click_link": "alto", "reply": "medio", "ignore": "bajo", "report": "bajo"}
    risk_level = risk_map.get(user_action, "medio")

    action_display = {
        "click_link": "Abrió el enlace",
        "reply": "Respondió el correo",
        "ignore": "Ignoró el correo",
        "report": "Reportó como phishing",
    }

    return render_template(
        "result.html",
        ai_analysis=ai_result["analysis"],
        ai_tip=ai_result["tip"],
        points=ai_result["points"],
        user_action=action_display.get(user_action, user_action),
        correct_action=action_display.get(scenario["correct_action"], scenario["correct_action"]),
        risk_level=risk_level,
        red_flags=scenario["clues"],
    )
    
@simulation.route("/save_quiz", methods=["POST"])
@login_required
def save_quiz():
    score = request.form.get("score", type=int)
    correct_count = request.form.get("correct", type=int)
    total = request.form.get("total", type=int)

    result = QuizResult(
        user_id=current_user.id,
        score=score,
        correct=correct_count,
        total=total
    )
    db.session.add(result)
    db.session.commit()

    return "Resultado guardado correctamente"
