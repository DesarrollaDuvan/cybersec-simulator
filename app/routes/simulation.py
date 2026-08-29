"""
app/routes/simulation.py
Simulador de ciberseguridad con dos módulos:
  - Phishing   (escenarios sc_001, sc_002, sc_003)
  - Contraseñas (escenarios pw_001, pw_002, pw_003)
"""

from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required
from app.services import SimulationService

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

    result = SimulationService.process_decision(scenario_id, user_action)

    if "error" in result:
        return result["error"], 404

    return render_template(
        "result.html",
        ai_analysis=result["ai_analysis"],
        ai_tip=result["ai_tip"],
        points=result["points"],
        user_action=result["user_action"],
        correct_action=result["correct_action"],
        risk_level=result["risk_level"],
        red_flags=result["red_flags"],
        module=result["module"],
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