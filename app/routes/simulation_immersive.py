"""
app/routes/simulation_immersive.py
Blueprint para las simulaciones inmersivas de ingeniería social y redes.

Registrar en __init__.py:
    from app.routes.simulation_immersive import sim_immersive
    app.register_blueprint(sim_immersive, url_prefix='/sim')
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.data import get_social_scenarios, get_network_scenarios
from app.services.immersive_service import ImmersiveService


sim_immersive = Blueprint("sim_immersive", __name__)


@sim_immersive.route("/")
@login_required
def home():
    return render_template("sim_home.html",
        social_scenarios=get_social_scenarios(),
        network_scenarios=get_network_scenarios(),
    )


# Redirigir /simulation a /sim para compatibilidad con navbar
@sim_immersive.route("/redirect-classic")
@login_required
def redirect_classic():
    return redirect(url_for('sim_immersive.home'))


@sim_immersive.route("/<scenario_id>")
@login_required
def play(scenario_id):
    result = ImmersiveService.start_simulation(scenario_id)
    if result is None:
        return "Escenario no encontrado", 404
    if result.get("completed"):
        return redirect(url_for('sim_immersive.results', scenario_id=scenario_id))

    return render_template("sim_play.html", scenario=result["scenario"], stage_index=result["stage_index"])


@sim_immersive.route("/decision", methods=["POST"])
@login_required
def decision():
    data = request.get_json()
    scenario_id = data.get("scenario_id")
    stage_id = data.get("stage_id")
    choice_id = data.get("choice_id")

    result = ImmersiveService.process_decision(scenario_id, stage_id, choice_id)
    if result is None:
        return jsonify({"error": "Escenario no encontrado"}), 404

    return jsonify(result)


@sim_immersive.route("/<scenario_id>/results")
@login_required
def results(scenario_id):
    result = ImmersiveService.get_results(scenario_id)
    if result is None:
        return redirect(url_for('sim_immersive.home'))

    return render_template("sim_results.html",
        scenario=result["scenario"],
        total_points=result["total_points"],
        max_points=result["max_points"],
        score_pct=result["score_pct"],
    )