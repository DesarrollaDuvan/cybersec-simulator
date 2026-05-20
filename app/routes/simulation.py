"""
app/routes/simulation.py
"""

import json
import random
from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from app.ai.gemini_client import ask_gemini_json
from app.models.progress import SimulationResult
from app import db

simulation = Blueprint("simulation", __name__)

# ── Escenarios ──────────────────────────────────────────────────────────────
# IMPORTANTE: Los links ahora apuntan a rutas internas de la simulación
# para que el usuario viva la experiencia del phishing en ambiente controlado.

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
        # ← Apunta a la página de phishing falsa del banco
        "link": "/simulation/trap/banco",
        "link_display": "http://banco-seguro-col.net/verificar?token=abc123",
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
        "link_display": None,
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
        # ← Apunta a la página de phishing falsa de Netflix
        "link": "/simulation/trap/netflix",
        "link_display": "http://netflix-pagos.com/update",
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

ACTION_LABELS = {
    "click_link": "Abrió el enlace sospechoso",
    "reply":      "Respondió el correo con información",
    "ignore":     "Ignoró y eliminó el correo",
    "report":     "Reportó el correo como phishing",
}

ACTION_DISPLAY = {
    "click_link": "Abrió el enlace",
    "reply":      "Respondió el correo",
    "ignore":     "Ignoró el correo",
    "report":     "Reportó como phishing",
}

RISK_MAP = {
    "click_link": "alto",
    "reply":      "medio",
    "ignore":     "bajo",
    "report":     "bajo",
}


def get_scenario(scenario_id=None):
    if scenario_id:
        return next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    return random.choice(SCENARIOS)


# ── Análisis con Gemini ─────────────────────────────────────────────────────

def analyze_decision(scenario: dict, user_action: str) -> dict:
    prompt = f"""Eres CyberTutor IA, experto en ciberseguridad que enseña a identificar phishing.
Un usuario enfrentó este escenario de simulación:

ESCENARIO:
- Remitente: {scenario['sender']}
- Asunto: {scenario['subject']}
- Cuerpo: {scenario['body']}
- Enlace visible: {scenario.get('link_display', 'Ninguno')}
- Señales reales de alerta: {', '.join(scenario['clues'])}
- Acción correcta: {scenario['correct_action']}

DECISIÓN DEL USUARIO: {ACTION_LABELS.get(user_action, user_action)}

Responde ÚNICAMENTE con JSON válido, sin markdown ni texto adicional:
{{
  "analysis": "Explicación de 3-4 oraciones sobre si la decisión fue correcta o no, mencionando señales concretas del correo.",
  "tip": "Consejo práctico de 1-2 oraciones para situaciones similares.",
  "points": <entero 0-100>
}}

Puntuación:
- report cuando era correcto: 100
- report cuando correct_action era ignore: 90
- ignore cuando era correcto: 75
- reply: 25
- click_link: 0
"""
    try:
        return ask_gemini_json(prompt)
    except Exception:
        return {
            "analysis": "No se pudo conectar con CyberTutor IA. Revisa tu GEMINI_API_KEY.",
            "tip": "Verifica siempre el dominio del remitente antes de hacer clic en cualquier enlace.",
            "points": 0,
        }


# ── Rutas ───────────────────────────────────────────────────────────────────

@simulation.route("/")
@login_required
def start():
    """Muestra un escenario de phishing al usuario."""
    scenario = get_scenario()
    session["current_scenario"] = scenario["id"]
    return render_template("simulation.html", scenario=scenario)


@simulation.route("/decision", methods=["POST"])
@login_required
def decision():
    """Procesa la decisión del usuario (botones de acción)."""
    user_action = request.form.get("action", "")
    scenario_id = request.form.get("scenario_id") or session.get("current_scenario")

    scenario = get_scenario(scenario_id)
    if not scenario:
        return "Escenario no encontrado", 404

    ai_result = analyze_decision(scenario, user_action)

    # Guardar resultado en BD
    try:
        sim_record = SimulationResult(
            user_id=current_user.id,
            scenario_id=scenario["id"],
            action_taken=user_action,
            is_correct=(
                user_action == scenario["correct_action"] or
                (user_action == "report" and scenario["correct_action"] == "ignore")
            ),
            points=ai_result["points"],
            risk_level=RISK_MAP.get(user_action, "medio"),
        )
        db.session.add(sim_record)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return render_template(
        "result.html",
        ai_analysis=ai_result["analysis"],
        ai_tip=ai_result["tip"],
        points=ai_result["points"],
        user_action=ACTION_DISPLAY.get(user_action, user_action),
        correct_action=ACTION_DISPLAY.get(scenario["correct_action"], scenario["correct_action"]),
        risk_level=RISK_MAP.get(user_action, "medio"),
        red_flags=scenario["clues"],
    )


# ── RUTAS DE TRAMPAS DE PHISHING ────────────────────────────────────────────

@simulation.route("/trap/banco")
@login_required
def trap_banco():
    """
    Página falsa de banco (trampa).
    Si el usuario llegó aquí, hizo clic en el enlace del phishing.
    Registra automáticamente la acción como 'click_link'.
    """
    scenario_id = session.get("current_scenario")
    scenario = get_scenario(scenario_id)

    # Registrar que el usuario cayó en la trampa
    if scenario:
        _register_trap_click(scenario, "click_link")

    return render_template("phishing_banco.html")


@simulation.route("/trap/netflix")
@login_required
def trap_netflix():
    """Página falsa de Netflix (trampa)."""
    scenario_id = session.get("current_scenario")
    scenario = get_scenario(scenario_id)

    if scenario:
        _register_trap_click(scenario, "click_link")

    return render_template("phishing_netflix.html")


@simulation.route("/phishing-caught")
@login_required
def phishing_caught():
    """
    Página educativa que se muestra después de que el usuario
    ingresó datos en la página de phishing falsa.
    """
    phishing_type = request.args.get("type", "banco")

    # Registrar en BD como click_link con 0 puntos si no se hizo ya
    scenario_id = session.get("current_scenario")
    scenario = get_scenario(scenario_id)
    if scenario:
        _register_trap_click(scenario, "click_link", force=False)

    return render_template("phishing_caught.html", phishing_type=phishing_type)


def _register_trap_click(scenario: dict, action: str, force: bool = True):
    """
    Registra en la BD que el usuario hizo clic en el enlace trampa.
    force=False evita duplicados si ya se registró.
    """
    if not force:
        # Verificar si ya existe un registro para este escenario en esta sesión
        existing = SimulationResult.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario["id"],
            action_taken=action,
        ).first()
        if existing:
            return

    try:
        sim_record = SimulationResult(
            user_id=current_user.id,
            scenario_id=scenario["id"],
            action_taken=action,
            is_correct=False,
            points=0,
            risk_level="alto",
        )
        db.session.add(sim_record)
        db.session.commit()
    except Exception:
        db.session.rollback()
