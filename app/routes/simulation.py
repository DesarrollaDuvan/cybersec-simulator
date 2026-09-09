"""
app/routes/simulation.py
Simulador de ciberseguridad con dos módulos:
  - Phishing   (escenarios sc_001, sc_002, sc_003)
  - Contraseñas (escenarios pw_001, pw_002, pw_003)
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, Response
from flask_login import login_required, current_user
from app.services import SimulationService
from app.ai import get_ai_client
from app.data import get_scenario_by_id
from app.constants import RISK_MAP
from app.extensions import csrf
import json
import logging

simulation = Blueprint("simulation", __name__)


@simulation.route("/")
@login_required
def start():
    """Pantalla de selección de módulo."""
    return render_template("simulation_home.html")


@simulation.route("/phishing")
@login_required
def start_phishing():
    """Inicia un escenario de phishing aleatorio."""
    scenario = SimulationService.start_simulation("phishing")
    if not scenario:
        return "No hay escenarios disponibles", 404
    return render_template("simulation.html", scenario=scenario)


@simulation.route("/passwords")
@login_required
def start_passwords():
    """Inicia un escenario de contraseñas aleatorio."""
    scenario = SimulationService.start_simulation("passwords")
    if not scenario:
        return "No hay escenarios disponibles", 404
    return render_template("simulation_password.html", scenario=scenario)


@simulation.route("/decision", methods=["POST"])
@login_required
def decision():
    """Procesa la decisión del usuario para ambos módulos."""
    user_action = request.form.get("action", "")
    scenario_id = request.form.get("scenario_id") or session.get("current_scenario")

    if not scenario_id:
        return "Escenario no encontrado", 404

    scenario = get_scenario_by_id(scenario_id)
    if not scenario:
        return "Escenario no encontrado", 404

    module = scenario.get("module", "phishing")

    # Basic validation only (no AI call) - AI will be streamed via SSE
    is_correct = (
        user_action == scenario["correct_action"] or
        (module == "phishing" and user_action == "report" and scenario["correct_action"] == "ignore")
    )

    # Quick local scoring (fallback if AI fails)
    if module == "passwords":
        points = 100 if is_correct else 10
    else:
        points = 100 if is_correct else 0

    # Determine display labels
    if module == "passwords":
        from app.constants import PASSWORD_ACTION_LABELS
        action_display = PASSWORD_ACTION_LABELS.get(user_action, user_action)
        correct_display = PASSWORD_ACTION_LABELS.get(
            scenario["correct_action"], scenario["correct_action"]
        )
    else:
        from app.constants import PHISHING_ACTION_DISPLAY
        action_display = PHISHING_ACTION_DISPLAY.get(user_action, user_action)
        correct_display = PHISHING_ACTION_DISPLAY.get(
            scenario["correct_action"], scenario["correct_action"]
        )

    # Save to DB immediately
    from flask_login import current_user
    from app.extensions import db
    from app.models.progress import SimulationResult
    import logging
    logger = logging.getLogger(__name__)

    try:
        record = SimulationResult(
            user_id=current_user.id,
            scenario_id=scenario["id"],
            action_taken=user_action,
            is_correct=is_correct,
            points=points,
            risk_level=RISK_MAP.get(user_action, "medio"),
        )
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        logger.exception("Error guardando SimulationResult: %s", e)
        db.session.rollback()

    # Return template with empty AI fields - frontend will stream via SSE
    return render_template(
        "result.html",
        ai_analysis="",      # Empty - will be filled via SSE
        ai_tip="",           # Empty - will be filled via SSE
        points=points,
        user_action=action_display,
        correct_action=correct_display,
        risk_level=RISK_MAP.get(user_action, "medio"),
        red_flags=scenario["clues"],
        module=module,
        scenario_id=scenario_id,
        user_action_raw=user_action,
    )


@simulation.route("/decision/stream", methods=["GET", "POST"])
@login_required
@csrf.exempt
def decision_stream():
    """SSE endpoint for streaming AI analysis."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"SSE request: method={request.method}, args={dict(request.args)}, session_user={getattr(current_user, 'id', None)}")
    
    # Support both GET (EventSource) and POST (direct call)
    if request.method == "GET":
        user_action = request.args.get("action", "")
        scenario_id = request.args.get("scenario_id") or session.get("current_scenario")
    else:
        user_action = request.form.get("action", "")
        scenario_id = request.form.get("scenario_id") or session.get("current_scenario")

    if not scenario_id:
        logger.warning("SSE: No scenario_id")
        return "Escenario no encontrado", 404

    scenario = get_scenario_by_id(scenario_id)
    if not scenario:
        logger.warning(f"SSE: Scenario not found: {scenario_id}")
        return "Escenario no encontrado", 404

    module = scenario.get("module", "phishing")

    def generate():
        import logging
        logger = logging.getLogger(__name__)
        client = get_ai_client()
        if module == "passwords":
            stream = client.analyze_password_stream(scenario, user_action)
        else:
            stream = client.analyze_phishing_stream(scenario, user_action)

        try:
            for chunk in stream:
                yield chunk
        except Exception as e:
            logger.exception("Error in SSE stream generator: %s", e)
            yield f"data: {json.dumps({'type': 'error', 'content': f'Error: {str(e)}'})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


# ── Trampas de phishing ─────────────────────────────────────────────────────

@simulation.route("/trap/banco")
@login_required
def trap_banco():
    scenario_id = session.get("current_scenario")
    if scenario_id:
        SimulationService.register_trap_click(scenario_id)
    return render_template("phishing_banco.html")


@simulation.route("/trap/netflix")
@login_required
def trap_netflix():
    scenario_id = session.get("current_scenario")
    if scenario_id:
        SimulationService.register_trap_click(scenario_id)
    return render_template("phishing_netflix.html")


@simulation.route("/phishing-caught")
@login_required
def phishing_caught():
    scenario_id = session.get("current_scenario")
    if scenario_id:
        SimulationService.register_trap_click(scenario_id, force=False)
    phishing_type = request.args.get("type", "banco")
    return render_template("phishing_caught.html", phishing_type=phishing_type)