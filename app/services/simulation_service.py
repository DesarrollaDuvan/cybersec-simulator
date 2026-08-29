"""
app/services/simulation_service.py
Lógica de negocio para simulaciones clásicas (phishing, contraseñas).
"""

import logging
from datetime import datetime
from flask import session
from flask_login import current_user

from app.extensions import db
from app.models.progress import SimulationResult
from app.ai import analyze_phishing, analyze_password
from app.data import get_scenario_by_id, get_random_scenario
from app.constants import (
    PHISHING_ACTION_LABELS,
    PHISHING_ACTION_DISPLAY,
    PASSWORD_ACTION_LABELS,
    RISK_MAP,
)

logger = logging.getLogger(__name__)


class SimulationService:
    """Servicio para gestionar simulaciones clásicas."""

    @staticmethod
    def start_simulation(module: str) -> dict | None:
        """
        Inicia una simulación aleatoria del módulo dado.

        Args:
            module: 'phishing' o 'passwords'

        Returns:
            dict con el escenario o None si error
        """
        scenario = get_random_scenario(module=module)
        if scenario:
            session["current_scenario"] = scenario["id"]
        return scenario

    @staticmethod
    def get_current_scenario(scenario_id: str = None) -> dict | None:
        """Obtiene el escenario actual por ID o de la sesión."""
        if not scenario_id:
            scenario_id = session.get("current_scenario")
        if not scenario_id:
            return None
        return get_scenario_by_id(scenario_id)

    @staticmethod
    def process_decision(scenario_id: str, user_action: str) -> dict:
        """
        Procesa la decisión del usuario y guarda el resultado.

        Args:
            scenario_id: ID del escenario
            user_action: acción tomada por el usuario

        Returns:
            dict con análisis de IA, puntos, y metadatos para template
        """
        scenario = get_scenario_by_id(scenario_id)
        if not scenario:
            return {"error": "Escenario no encontrado"}

        module = scenario.get("module", "phishing")

        # Analizar con IA
        if module == "passwords":
            ai_result = analyze_password(scenario, user_action)
            action_display = PASSWORD_ACTION_LABELS.get(user_action, user_action)
            correct_display = PASSWORD_ACTION_LABELS.get(
                scenario["correct_action"], scenario["correct_action"]
            )
        else:
            ai_result = analyze_phishing(scenario, user_action)
            action_display = PHISHING_ACTION_DISPLAY.get(user_action, user_action)
            correct_display = PHISHING_ACTION_DISPLAY.get(
                scenario["correct_action"], scenario["correct_action"]
            )

        # Determinar si fue correcto
        is_correct = (
            user_action == scenario["correct_action"] or
            (module == "phishing" and user_action == "report" and scenario["correct_action"] == "ignore")
        )

        # Guardar en BD
        try:
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
        except Exception as e:
            logger.exception("Error guardando SimulationResult: %s", e)
            db.session.rollback()

        return {
            "ai_analysis": ai_result["analysis"],
            "ai_tip": ai_result["tip"],
            "points": ai_result["points"],
            "user_action": action_display,
            "correct_action": correct_display,
            "risk_level": RISK_MAP.get(user_action, "medio"),
            "red_flags": scenario["clues"],
            "module": module,
            "is_correct": is_correct,
        }

    @staticmethod
    def register_trap_click(scenario_id: str, force: bool = True) -> bool:
        """
        Registra que el usuario cayó en una trampa (click_link).

        Args:
            scenario_id: ID del escenario
            force: si True, registra aunque ya exista

        Returns:
            bool indicando si se registró
        """
        scenario = get_scenario_by_id(scenario_id)
        if not scenario:
            return False

        if not force:
            existing = SimulationResult.query.filter_by(
                user_id=current_user.id,
                scenario_id=scenario["id"],
                action_taken="click_link",
            ).first()
            if existing:
                return False

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
            return True
        except Exception as e:
            logger.exception("Error registrando trap click: %s", e)
            db.session.rollback()
            return False

    @staticmethod
    def get_user_stats(user_id: int = None) -> dict:
        """Obtiene estadísticas de simulaciones del usuario."""
        if user_id is None:
            user_id = current_user.id

        results = SimulationResult.query.filter_by(user_id=user_id).all()

        if not results:
            return {
                "total": 0,
                "correct": 0,
                "accuracy": 0,
                "avg_points": 0,
                "by_module": {},
                "by_risk": {},
            }

        total = len(results)
        correct = sum(1 for r in results if r.is_correct)
        avg_points = sum(r.points for r in results) / total

        by_module = {}
        by_risk = {}

        for r in results:
            module = r.scenario_id[:2]  # sc_, pw_, is_, net_
            if module not in by_module:
                by_module[module] = {"total": 0, "correct": 0}
            by_module[module]["total"] += 1
            if r.is_correct:
                by_module[module]["correct"] += 1

            risk = r.risk_level
            if risk not in by_risk:
                by_risk[risk] = 0
            by_risk[risk] += 1

        return {
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total * 100) if total > 0 else 0,
            "avg_points": round(avg_points),
            "by_module": by_module,
            "by_risk": by_risk,
        }