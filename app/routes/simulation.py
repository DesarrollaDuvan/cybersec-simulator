"""
app/routes/simulation.py
Simulador de ciberseguridad con dos módulos:
  - Phishing   (escenarios sc_001, sc_002, sc_003)
  - Contraseñas (escenarios pw_001, pw_002, pw_003)
"""

import json
import random
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user
from app.ai.gemini_client import ask_gemini_json
from app.models.progress import SimulationResult
from app import db

simulation = Blueprint("simulation", __name__)

# ════════════════════════════════════════════════════════════════
# ESCENARIOS DE PHISHING
# ════════════════════════════════════════════════════════════════

PHISHING_SCENARIOS = [
    {
        "id": "sc_001",
        "module": "phishing",
        "sender": "soporte@banco-seguro-col.net",
        "subject": "⚠ Urgente: Su cuenta ha sido bloqueada",
        "body": (
            "Estimado cliente, hemos detectado actividad sospechosa en su cuenta. "
            "Para evitar el bloqueo permanente, debe verificar su identidad en las "
            "próximas 24 horas. Haga clic en el enlace para actualizar sus datos."
        ),
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
        "module": "phishing",
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
        "module": "phishing",
        "sender": "no-reply@netflix.com",
        "subject": "Tu suscripción expira hoy — Actualiza tu método de pago",
        "body": (
            "Tu suscripción a Netflix está a punto de expirar. Para seguir disfrutando "
            "de tu contenido favorito sin interrupciones, actualiza tu método de pago "
            "ahora. Si no lo haces, tu cuenta será cancelada esta noche."
        ),
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

# ════════════════════════════════════════════════════════════════
# ESCENARIOS DE CONTRASEÑAS
# ════════════════════════════════════════════════════════════════

PASSWORD_SCENARIOS = [
    {
        "id": "pw_001",
        "module": "passwords",
        "title": "Creando una cuenta nueva",
        "context": (
            "Estás registrándote en el portal de tu empresa. "
            "El sistema te pide crear una contraseña. "
            "¿Cuál de estas opciones elegirías?"
        ),
        "password_options": [
            {"id": "a", "value": "juan1990",         "label": "juan1990"},
            {"id": "b", "value": "123456",            "label": "123456"},
            {"id": "c", "value": "Tr0pico#Azul!2024", "label": "Tr0pico#Azul!2024"},
            {"id": "d", "value": "empresa2024",       "label": "empresa2024"},
        ],
        "correct_action": "choose_strong",    # elegir la contraseña fuerte
        "correct_option": "c",
        "risk": "alto",
        "question": "¿Cuál contraseña es la más segura?",
        "clues": [
            "'juan1990' usa información personal predecible (nombre + año)",
            "'123456' es la contraseña más hackeada del mundo",
            "'empresa2024' es predecible y corta",
            "'Tr0pico#Azul!2024' tiene mayúsculas, minúsculas, números y símbolos (+12 chars)",
        ],
        "actions": [
            {"id": "choose_strong", "label": "Tr0pico#Azul!2024 ✓", "style": "safe"},
            {"id": "choose_common", "label": "123456 o juan1990",   "style": "danger"},
            {"id": "use_name",      "label": "Mi nombre + año",     "style": "warning"},
            {"id": "reuse_old",     "label": "Reutilizar una vieja", "style": "danger"},
        ],
    },
    {
        "id": "pw_002",
        "module": "passwords",
        "title": "Te piden cambiar tu contraseña",
        "context": (
            "Tu empresa exige cambiar la contraseña cada 90 días. "
            "Ya usaste 'MiClave2024!' el trimestre pasado. "
            "¿Qué harías?"
        ),
        "password_options": [
            {"id": "a", "value": "MiClave2025!",           "label": "MiClave2025!  (solo cambio el año)"},
            {"id": "b", "value": "K#9mPx!vQ2@nL",          "label": "K#9mPx!vQ2@nL  (nueva aleatoria)"},
            {"id": "c", "value": "MiClave2024!",            "label": "MiClave2024!  (la misma de siempre)"},
            {"id": "d", "value": "NombreMascota123",        "label": "NombreMascota123"},
        ],
        "correct_action": "use_manager",
        "correct_option": "b",
        "risk": "medio",
        "question": "¿Cuál es la mejor práctica al cambiar contraseña?",
        "clues": [
            "Cambiar solo el año ('2024' → '2025') es predecible y fácil de adivinar",
            "Reutilizar la misma contraseña la expone si ya fue filtrada",
            "Información personal como mascotas aparece en ataques de diccionario",
            "Una contraseña aleatoria generada por un gestor es la opción más segura",
        ],
        "actions": [
            {"id": "use_manager",   "label": "Usar gestor y generar nueva aleatoria", "style": "safe"},
            {"id": "increment_year","label": "Cambiar solo el año al final",          "style": "warning"},
            {"id": "reuse",         "label": "Usar la misma de siempre",              "style": "danger"},
            {"id": "use_personal",  "label": "Usar datos personales",                 "style": "danger"},
        ],
    },
    {
        "id": "pw_003",
        "module": "passwords",
        "title": "Un compañero te pide tu contraseña",
        "context": (
            "Tu compañero de trabajo dice que necesita acceder urgentemente "
            "al sistema mientras tú no estás, y te pide que le des tu contraseña "
            "temporalmente por WhatsApp. ¿Qué haces?"
        ),
        "password_options": None,   # Este escenario es de decisión, no de elección de contraseña
        "correct_action": "refuse_and_report",
        "correct_option": None,
        "risk": "alto",
        "question": "¿Cuál es la respuesta correcta?",
        "clues": [
            "Las contraseñas son personales e intransferibles, sin excepción",
            "Compartir por WhatsApp las expone a terceros y al historial del chat",
            "Puede ser un ataque de ingeniería social, incluso si conoces a la persona",
            "La solución correcta es gestionar accesos temporales con el administrador de TI",
        ],
        "actions": [
            {"id": "refuse_and_report", "label": "Negarme y escalar a TI",              "style": "safe"},
            {"id": "share_whatsapp",    "label": "Enviarla por WhatsApp",               "style": "danger"},
            {"id": "share_verbal",      "label": "Decírsela en persona",                "style": "danger"},
            {"id": "create_temp",       "label": "Crear una temporal yo mismo",         "style": "warning"},
        ],
    },
]

# Combinar todos los escenarios
ALL_SCENARIOS = PHISHING_SCENARIOS + PASSWORD_SCENARIOS

# ════════════════════════════════════════════════════════════════
# LABELS Y MAPAS
# ════════════════════════════════════════════════════════════════

PHISHING_ACTION_LABELS = {
    "click_link": "Abrió el enlace sospechoso",
    "reply":      "Respondió el correo con información",
    "ignore":     "Ignoró y eliminó el correo",
    "report":     "Reportó el correo como phishing",
}

PHISHING_ACTION_DISPLAY = {
    "click_link": "Abrió el enlace",
    "reply":      "Respondió el correo",
    "ignore":     "Ignoró el correo",
    "report":     "Reportó como phishing",
}

PASSWORD_ACTION_LABELS = {
    "choose_strong":    "Eligió la contraseña más fuerte",
    "choose_common":    "Eligió una contraseña común o predecible",
    "use_name":         "Eligió usar nombre y año",
    "reuse_old":        "Reutilizó una contraseña anterior",
    "use_manager":      "Usó un gestor para generar contraseña aleatoria",
    "increment_year":   "Solo cambió el año al final de la contraseña",
    "reuse":            "Reutilizó exactamente la misma contraseña",
    "use_personal":     "Usó información personal como contraseña",
    "refuse_and_report":"Se negó a compartir y escaló a TI",
    "share_whatsapp":   "Compartió la contraseña por WhatsApp",
    "share_verbal":     "Dijo la contraseña en persona",
    "create_temp":      "Creó una contraseña temporal por su cuenta",
}

RISK_MAP = {
    # Phishing
    "click_link": "alto",  "reply": "medio",
    "ignore":     "bajo",  "report": "bajo",
    # Contraseñas — acciones correctas
    "choose_strong":    "bajo",
    "use_manager":      "bajo",
    "refuse_and_report":"bajo",
    # Contraseñas — acciones incorrectas
    "choose_common":    "alto",
    "use_name":         "alto",
    "reuse_old":        "alto",
    "increment_year":   "medio",
    "reuse":            "alto",
    "use_personal":     "alto",
    "share_whatsapp":   "alto",
    "share_verbal":     "alto",
    "create_temp":      "medio",
}


def get_scenario(scenario_id=None, module=None):
    """Retorna escenario por ID, por módulo (aleatorio), o completamente aleatorio."""
    if scenario_id:
        return next((s for s in ALL_SCENARIOS if s["id"] == scenario_id), None)
    if module == "phishing":
        return random.choice(PHISHING_SCENARIOS)
    if module == "passwords":
        return random.choice(PASSWORD_SCENARIOS)
    return random.choice(ALL_SCENARIOS)


# ════════════════════════════════════════════════════════════════
# ANÁLISIS CON IA
# ════════════════════════════════════════════════════════════════

def analyze_phishing(scenario: dict, user_action: str) -> dict:
    prompt = f"""Eres CyberTutor IA, experto en ciberseguridad que enseña a identificar phishing.

ESCENARIO:
- Remitente: {scenario['sender']}
- Asunto: {scenario['subject']}
- Cuerpo: {scenario['body']}
- Enlace visible: {scenario.get('link_display', 'Ninguno')}
- Señales de alerta: {', '.join(scenario['clues'])}
- Acción correcta: {scenario['correct_action']}

DECISIÓN DEL USUARIO: {PHISHING_ACTION_LABELS.get(user_action, user_action)}

Responde ÚNICAMENTE con JSON válido sin markdown:
{{
  "analysis": "Explicación de 3-4 oraciones mencionando señales concretas del correo.",
  "tip": "Consejo práctico de 1-2 oraciones.",
  "points": <0-100>
}}

Puntuación: report correcto=100, report cuando debía ignorar=90, ignore correcto=75, reply=25, click_link=0"""
    try:
        return ask_gemini_json(prompt)
    except Exception:
        return {
            "analysis": "No se pudo conectar con la IA. Verifica tu API key.",
            "tip": "Verifica siempre el dominio del remitente antes de hacer clic.",
            "points": 0,
        }


def analyze_password(scenario: dict, user_action: str) -> dict:
    is_correct = (user_action == scenario["correct_action"])

    prompt = f"""Eres CyberTutor IA, experto en ciberseguridad que enseña buenas prácticas de contraseñas.

ESCENARIO: {scenario['title']}
CONTEXTO: {scenario['context']}
PISTAS CLAVE: {', '.join(scenario['clues'])}
ACCIÓN CORRECTA: {scenario['correct_action']} — {PASSWORD_ACTION_LABELS.get(scenario['correct_action'], '')}
DECISIÓN DEL USUARIO: {PASSWORD_ACTION_LABELS.get(user_action, user_action)}
¿FUE CORRECTA?: {'Sí' if is_correct else 'No'}

Responde ÚNICAMENTE con JSON válido sin markdown:
{{
  "analysis": "Explicación de 3-4 oraciones educativas sobre por qué la decisión fue correcta o incorrecta, con contexto de seguridad real.",
  "tip": "Consejo práctico y accionable de 1-2 oraciones para aplicar en el día a día.",
  "points": <0-100>
}}

Puntuación según acción:
- Acción correcta: 100
- Acción con riesgo medio (create_temp, increment_year): 40
- Acción peligrosa (share, reuse, use_personal, choose_common): 0-15"""
    try:
        return ask_gemini_json(prompt)
    except Exception:
        points = 100 if is_correct else 10
        return {
            "analysis": "No se pudo conectar con la IA en este momento.",
            "tip": "Usa un gestor de contraseñas para crear y guardar contraseñas únicas por cada sitio.",
            "points": points,
        }


# ════════════════════════════════════════════════════════════════
# RUTAS
# ════════════════════════════════════════════════════════════════

@simulation.route("/")
@login_required
def start():
    """Pantalla de selección de módulo."""
    return render_template("simulation_home.html")


@simulation.route("/phishing")
@login_required
def start_phishing():
    """Inicia un escenario de phishing aleatorio."""
    scenario = get_scenario(module="phishing")
    session["current_scenario"] = scenario["id"]
    return render_template("simulation.html", scenario=scenario)


@simulation.route("/passwords")
@login_required
def start_passwords():
    """Inicia un escenario de contraseñas aleatorio."""
    scenario = get_scenario(module="passwords")
    session["current_scenario"] = scenario["id"]
    return render_template("simulation_password.html", scenario=scenario)


@simulation.route("/decision", methods=["POST"])
@login_required
def decision():
    """Procesa la decisión del usuario para ambos módulos."""
    user_action = request.form.get("action", "")
    scenario_id = request.form.get("scenario_id") or session.get("current_scenario")

    scenario = get_scenario(scenario_id)
    if not scenario:
        return "Escenario no encontrado", 404

    module = scenario.get("module", "phishing")

    # Llamar al analizador correcto según el módulo
    if module == "passwords":
        ai_result = analyze_password(scenario, user_action)
        action_display = PASSWORD_ACTION_LABELS.get(user_action, user_action)
        correct_display = PASSWORD_ACTION_LABELS.get(scenario["correct_action"], scenario["correct_action"])
    else:
        ai_result = analyze_phishing(scenario, user_action)
        action_display = PHISHING_ACTION_DISPLAY.get(user_action, user_action)
        correct_display = PHISHING_ACTION_DISPLAY.get(scenario["correct_action"], scenario["correct_action"])

    # Guardar en BD
    try:
        is_correct = (
            user_action == scenario["correct_action"] or
            (module == "phishing" and user_action == "report" and scenario["correct_action"] == "ignore")
        )
        record = SimulationResult(
            user_id=current_user.id,
            scenario_id=scenario["id"],
            action_taken=user_action,
            is_correct=is_correct,
            points=ai_result["points"],
            risk_level=RISK_MAP.get(user_action, "medio"),
        )
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return render_template(
        "result.html",
        ai_analysis=ai_result["analysis"],
        ai_tip=ai_result["tip"],
        points=ai_result["points"],
        user_action=action_display,
        correct_action=correct_display,
        risk_level=RISK_MAP.get(user_action, "medio"),
        red_flags=scenario["clues"],
        module=module,
    )


# ── Trampas de phishing ─────────────────────────────────────────────────────

@simulation.route("/trap/banco")
@login_required
def trap_banco():
    scenario_id = session.get("current_scenario")
    scenario = get_scenario(scenario_id)
    if scenario:
        _register_trap_click(scenario)
    return render_template("phishing_banco.html")


@simulation.route("/trap/netflix")
@login_required
def trap_netflix():
    scenario_id = session.get("current_scenario")
    scenario = get_scenario(scenario_id)
    if scenario:
        _register_trap_click(scenario)
    return render_template("phishing_netflix.html")


@simulation.route("/phishing-caught")
@login_required
def phishing_caught():
    phishing_type = request.args.get("type", "banco")
    scenario_id   = session.get("current_scenario")
    scenario      = get_scenario(scenario_id)
    if scenario:
        _register_trap_click(scenario, force=False)
    return render_template("phishing_caught.html", phishing_type=phishing_type)


def _register_trap_click(scenario: dict, force: bool = True):
    if not force:
        existing = SimulationResult.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario["id"],
            action_taken="click_link",
        ).first()
        if existing:
            return
    try:
        db.session.add(SimulationResult(
            user_id=current_user.id,
            scenario_id=scenario["id"],
            action_taken="click_link",
            is_correct=False,
            points=0,
            risk_level="alto",
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
