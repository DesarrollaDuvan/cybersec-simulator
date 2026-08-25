"""
app/routes/simulation_immersive.py
Blueprint para las simulaciones inmersivas de ingeniería social y redes.

Registrar en __init__.py:
    from app.routes.simulation_immersive import sim_immersive
    app.register_blueprint(sim_immersive, url_prefix='/sim')
"""

import json
import random
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.routes.simulation_scenarios import (
    SOCIAL_ENGINEERING_SCENARIOS,
    NETWORK_SCENARIOS,
    ALL_IMMERSIVE_SCENARIOS,
    get_immersive_scenario,
)

# IA — usa OpenRouter o Gemini según lo que tengas configurado
try:
    from app.ai.gemini_client import ask_gemini_json
    def analyze_choice(scenario, stage, choice_id):
        stage_info  = next(s for s in scenario["stages"] if s["id"] == stage)
        choice_info = next((c for c in stage_info.get("choices", []) if c["id"] == choice_id), {})
        is_correct  = (choice_id == stage_info["correct"])

        prompt = f"""Eres CyberTutor IA analizando una simulación de ciberseguridad.

Escenario: {scenario['title']}
Situación: {stage_info.get('scene_text', stage_info.get('transcript', ''))}
Decisión del usuario: {choice_info.get('label', choice_id)}
¿Fue correcta?: {'Sí' if is_correct else 'No'}
Consecuencia real: {stage_info['consequence_good' if is_correct else 'consequence_bad']}

Responde ÚNICAMENTE con JSON:
{{
  "verdict": "correcto" | "incorrecto" | "parcial",
  "explanation": "2-3 oraciones explicando el impacto real de esta decisión con datos concretos.",
  "lesson": "1 oración con la lección de seguridad clave.",
  "points": <0-100>
}}"""
        try:
            return ask_gemini_json(prompt)
        except Exception:
            return {
                "verdict": "correcto" if is_correct else "incorrecto",
                "explanation": stage_info["consequence_good" if is_correct else "consequence_bad"],
                "lesson": "Siempre verifica antes de actuar.",
                "points": 100 if is_correct else 0,
            }
except ImportError:
    def analyze_choice(scenario, stage, choice_id):
        stage_info = next(s for s in scenario["stages"] if s["id"] == stage)
        is_correct = (choice_id == stage_info["correct"])
        return {
            "verdict": "correcto" if is_correct else "incorrecto",
            "explanation": stage_info["consequence_good" if is_correct else "consequence_bad"],
            "lesson": "Piensa antes de actuar.",
            "points": 100 if is_correct else 0,
        }


sim_immersive = Blueprint("sim_immersive", __name__)


@sim_immersive.route("/")
@login_required
def home():
    return render_template("sim_home.html",
        social_scenarios=SOCIAL_ENGINEERING_SCENARIOS,
        network_scenarios=NETWORK_SCENARIOS,
    )

# Redirigir /simulation a /sim para compatibilidad con navbar
@sim_immersive.route("/redirect-classic")
@login_required
def redirect_classic():
    return redirect(url_for('sim_immersive.home'))


@sim_immersive.route("/<scenario_id>")
@login_required
def play(scenario_id):
    scenario = get_immersive_scenario(scenario_id)
    if not scenario:
        return "Escenario no encontrado", 404
    session["sim_scenario"] = scenario_id
    session["sim_stage"]    = 0
    session["sim_points"]   = 0
    return render_template("sim_play.html", scenario=scenario, stage_index=0)


@sim_immersive.route("/decision", methods=["POST"])
@login_required
def decision():
    data        = request.get_json()
    scenario_id = data.get("scenario_id")
    stage_id    = data.get("stage_id")
    choice_id   = data.get("choice_id")

    scenario = get_immersive_scenario(scenario_id)
    if not scenario:
        return jsonify({"error": "Escenario no encontrado"}), 404

    result = analyze_choice(scenario, stage_id, choice_id)

    # Avanzar al siguiente stage
    stage_ids   = [s["id"] for s in scenario["stages"]]
    current_idx = stage_ids.index(stage_id) if stage_id in stage_ids else 0
    next_idx    = current_idx + 1
    has_next    = next_idx < len(scenario["stages"])

    # Acumular puntos en sesión
    pts = session.get("sim_points", 0) + result.get("points", 0)
    session["sim_points"] = pts

    stage_info = next(s for s in scenario["stages"] if s["id"] == stage_id)
    is_correct = (choice_id == stage_info["correct"])

    return jsonify({
        "verdict":      result["verdict"],
        "explanation":  result["explanation"],
        "lesson":       result["lesson"],
        "points":       result["points"],
        "total_points": pts,
        "is_correct":   is_correct,
        "consequence":  stage_info["consequence_good" if is_correct else "consequence_bad"],
        "has_next":     has_next,
        "next_stage":   scenario["stages"][next_idx] if has_next else None,
        "next_index":   next_idx if has_next else None,
    })


@sim_immersive.route("/<scenario_id>/results")
@login_required
def results(scenario_id):
    scenario    = get_immersive_scenario(scenario_id)
    total_pts   = session.get("sim_points", 0)
    max_pts     = len(scenario["stages"]) * 100 if scenario else 100
    score_pct   = min(round(total_pts / max_pts * 100), 100)
    return render_template("sim_results.html",
        scenario=scenario,
        total_points=total_pts,
        max_points=max_pts,
        score_pct=score_pct,
    )