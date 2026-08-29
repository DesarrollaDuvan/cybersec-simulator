"""
app/services/immersive_service.py
Lógica de negocio para simulaciones inmersivas (multi-etapa).
"""

from datetime import datetime
from flask import session
from flask_login import current_user

from app.extensions import db
from app.models.progress import SimulationProgress
from app.ai import analyze_immersive
from app.data import get_scenario_by_id


class ImmersiveService:
    """Servicio para gestionar simulaciones inmersivas."""

    @staticmethod
    def get_or_create_progress(scenario_id: str) -> SimulationProgress:
        """Obtiene o crea el progreso de simulación para el usuario actual."""
        progress = SimulationProgress.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario_id
        ).first()

        if not progress:
            progress = SimulationProgress(
                user_id=current_user.id,
                scenario_id=scenario_id,
                current_stage=None,
                completed_stages=[],
                total_points=0,
                choices={},
                started_at=datetime.utcnow()
            )
            db.session.add(progress)
            db.session.commit()

        return progress

    @staticmethod
    def start_simulation(scenario_id: str) -> dict | None:
        """
        Inicia una simulación inmersiva.

        Args:
            scenario_id: ID del escenario

        Returns:
            dict con escenario y stage_index inicial
        """
        scenario = get_scenario_by_id(scenario_id)
        if not scenario:
            return None

        progress = ImmersiveService.get_or_create_progress(scenario_id)

        # Si ya completó, retornar None para redirigir a resultados
        if progress.is_completed:
            return {"completed": True}

        stage_ids = [s["id"] for s in scenario["stages"]]

        # Determinar stage inicial
        if progress.current_stage and progress.current_stage in stage_ids:
            stage_index = stage_ids.index(progress.current_stage)
        else:
            stage_index = 0
            progress.current_stage = stage_ids[0]
            db.session.commit()

        return {
            "scenario": scenario,
            "stage_index": stage_index,
            "progress": progress,
        }

    @staticmethod
    def process_decision(scenario_id: str, stage_id: str, choice_id: str) -> dict | None:
        """
        Procesa una decisión en simulación inmersiva.

        Args:
            scenario_id: ID del escenario
            stage_id: ID del stage actual
            choice_id: ID de la elección del usuario

        Returns:
            dict con resultado y metadatos para respuesta JSON
        """
        scenario = get_scenario_by_id(scenario_id)
        if not scenario:
            return None

        progress = ImmersiveService.get_or_create_progress(scenario_id)

        # Obtener info del stage y choice
        stage_info = next(s for s in scenario["stages"] if s["id"] == stage_id)
        choice_info = next((c for c in stage_info.get("choices", []) if c["id"] == choice_id), {})
        is_correct = (choice_id == stage_info["correct"])

        # Analizar con IA
        result = analyze_immersive(scenario, stage_info, choice_info, is_correct)

        # Actualizar progreso
        ImmersiveService._update_progress(progress, stage_id, choice_id, result.get("points", 0), is_correct, scenario)

        # Determinar siguiente stage
        stage_ids = [s["id"] for s in scenario["stages"]]
        current_idx = stage_ids.index(stage_id) if stage_id in stage_ids else 0
        next_idx = current_idx + 1
        has_next = next_idx < len(scenario["stages"])

        return {
            "verdict": result["verdict"],
            "explanation": result["explanation"],
            "lesson": result["lesson"],
            "points": result["points"],
            "total_points": progress.total_points,
            "is_correct": is_correct,
            "consequence": stage_info["consequence_good" if is_correct else "consequence_bad"],
            "has_next": has_next,
            "next_stage": scenario["stages"][next_idx] if has_next else None,
            "next_index": next_idx if has_next else None,
            "completed": not has_next,
        }

    @staticmethod
    def _update_progress(progress: SimulationProgress, stage_id: str, choice_id: str, points: int, is_correct: bool, scenario: dict) -> None:
        """Actualiza el progreso en base de datos."""
        if stage_id not in progress.completed_stages:
            progress.completed_stages.append(stage_id)

        progress.choices[stage_id] = choice_id
        progress.total_points += points

        stage_ids = [s["id"] for s in scenario["stages"]]
        current_idx = stage_ids.index(stage_id)
        next_idx = current_idx + 1

        if next_idx < len(stage_ids):
            progress.current_stage = stage_ids[next_idx]
        else:
            progress.current_stage = None
            progress.completed_at = datetime.utcnow()

        progress.updated_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def get_results(scenario_id: str) -> dict | None:
        """Obtiene los resultados finales de una simulación."""
        scenario = get_scenario_by_id(scenario_id)
        if not scenario:
            return None

        progress = SimulationProgress.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario_id
        ).first()

        if not progress:
            return None

        total_pts = progress.total_points
        max_pts = len(scenario["stages"]) * 100 if scenario else 100
        score_pct = min(round(total_pts / max_pts * 100), 100) if max_pts > 0 else 0

        return {
            "scenario": scenario,
            "total_points": total_pts,
            "max_points": max_pts,
            "score_pct": score_pct,
            "progress": progress,
        }

    @staticmethod
    def reset_progress(scenario_id: str) -> bool:
        """Reinicia el progreso de una simulación (para re-jugar)."""
        progress = SimulationProgress.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario_id
        ).first()

        if progress:
            db.session.delete(progress)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_history(user_id: int = None) -> list:
        """Obtiene historial de simulaciones inmersivas del usuario."""
        if user_id is None:
            user_id = current_user.id

        progresses = SimulationProgress.query.filter_by(user_id=user_id)\
            .order_by(SimulationProgress.started_at.desc()).all()

        return progresses