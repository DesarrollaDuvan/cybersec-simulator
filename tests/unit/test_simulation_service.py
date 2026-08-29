# tests/unit/test_simulation_service.py
import pytest
from unittest.mock import patch, MagicMock

from app.services.simulation_service import SimulationService
from app.data import get_scenario_by_id


class TestSimulationService:
    """Tests para SimulationService."""

    def test_get_scenario_by_id_exists(self):
        """Test que get_scenario_by_id retorna escenario existente."""
        scenario = get_scenario_by_id("sc_001")
        assert scenario is not None
        assert scenario["id"] == "sc_001"
        assert scenario["module"] == "phishing"

    def test_get_scenario_by_id_not_exists(self):
        """Test que get_scenario_by_id retorna None para ID inexistente."""
        scenario = get_scenario_by_id("nonexistent")
        assert scenario is None

    def test_get_all_phishing_scenarios(self):
        """Test que hay 3 escenarios de phishing."""
        from app.data import get_phishing_scenarios
        scenarios = get_phishing_scenarios()
        assert len(scenarios) == 3
        assert all(s["module"] == "phishing" for s in scenarios)

    def test_get_all_password_scenarios(self):
        """Test que hay 3 escenarios de contraseñas."""
        from app.data import get_password_scenarios
        scenarios = get_password_scenarios()
        assert len(scenarios) == 3
        assert all(s["module"] == "passwords" for s in scenarios)

    def test_get_all_immersive_scenarios(self):
        """Test que hay 6 escenarios inmersivos (3 social + 3 networks)."""
        from app.data import get_all_immersive_scenarios
        scenarios = get_all_immersive_scenarios()
        assert len(scenarios) == 6

    @patch("app.services.simulation_service.analyze_phishing")
    def test_process_decision_phishing_correct(self, mock_analyze, app, authenticated_user, client):
        """Test procesar decisión correcta en phishing."""
        mock_analyze.return_value = {
            "analysis": "Correcto, detectaste el phishing",
            "tip": "Siempre verifica el dominio",
            "points": 100
        }

        with app.app_context():
            # Iniciar simulación de phishing
            scenario = SimulationService.start_simulation("phishing")
            assert scenario is not None
            scenario_id = scenario["id"]

            # Procesar decisión correcta (report para sc_001)
            result = SimulationService.process_decision(scenario_id, "report")

            assert "ai_analysis" in result
            assert result["points"] == 100
            assert result["module"] == "phishing"
            assert result["is_correct"] is True

    @patch("app.services.simulation_service.analyze_password")
    def test_process_decision_password_correct(self, mock_analyze, app, authenticated_user, client):
        """Test procesar decisión correcta en contraseñas."""
        mock_analyze.return_value = {
            "analysis": "Correcto, elegiste la contraseña fuerte",
            "tip": "Usa gestor de contraseñas",
            "points": 100
        }

        with app.app_context():
            scenario = SimulationService.start_simulation("passwords")
            assert scenario is not None
            scenario_id = scenario["id"]

            # La acción correcta para pw_001 es "choose_strong"
            result = SimulationService.process_decision(scenario_id, "choose_strong")

            assert "ai_analysis" in result
            assert result["points"] == 100
            assert result["module"] == "passwords"
            assert result["is_correct"] is True

    def test_register_trap_click(self, app, authenticated_user, client):
        """Test registrar click en trampa de phishing."""
        with app.app_context():
            scenario = get_scenario_by_id("sc_001")
            scenario_id = scenario["id"]

            result = SimulationService.register_trap_click(scenario_id)
            assert result is True

            # Verificar que se guardó en BD
            from app.models.progress import SimulationResult
            record = SimulationResult.query.filter_by(
                user_id=authenticated_user.id,
                scenario_id=scenario_id,
                action_taken="click_link"
            ).first()
            assert record is not None
            assert record.is_correct is False
            assert record.points == 0