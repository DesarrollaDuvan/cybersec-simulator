# tests/integration/test_simulation_flow.py
import pytest
from unittest.mock import patch


class TestSimulationFlow:
    """Tests de integración para flujo de simulaciones."""

    @patch("app.services.simulation_service.analyze_phishing")
    def test_start_phishing_simulation(self, mock_analyze, client, authenticated_user):
        """Test iniciar simulación de phishing."""
        mock_analyze.return_value = {
            "analysis": "Test analysis",
            "tip": "Test tip",
            "points": 75
        }

        # Acceder a página de selección
        response = client.get("/simulation/")
        assert response.status_code == 200

        # Iniciar phishing
        response = client.get("/simulation/phishing", follow_redirects=True)
        assert response.status_code == 200
        assert b"simulation" in response.data.lower() or b"phishing" in response.data.lower()

    @patch("app.services.simulation_service.analyze_phishing")
    def test_start_password_simulation(self, mock_analyze, client, authenticated_user):
        """Test iniciar simulación de contraseñas."""
        mock_analyze.return_value = {
            "analysis": "Test analysis",
            "tip": "Test tip",
            "points": 100
        }

        response = client.get("/simulation/passwords", follow_redirects=True)
        assert response.status_code == 200

    @patch("app.services.simulation_service.analyze_phishing")
    def test_submit_phishing_decision(self, mock_analyze, client, authenticated_user):
        """Test enviar decisión en simulación de phishing."""
        mock_analyze.return_value = {
            "analysis": "Correcto",
            "tip": "Siempre verifica",
            "points": 100
        }

        # Primero iniciar simulación
        client.get("/simulation/phishing")

        # Enviar decisión
        response = client.post("/simulation/decision", data={
            "action": "report",
            "scenario_id": "sc_001",
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"result" in response.data.lower() or b"an.lisis" in response.data.lower()

    @patch("app.services.simulation_service.analyze_password")
    def test_submit_password_decision(self, mock_analyze, client, authenticated_user):
        """Test enviar decisión en simulación de contraseñas."""
        mock_analyze.return_value = {
            "analysis": "Correcto",
            "tip": "Usa gestor",
            "points": 100
        }

        client.get("/simulation/passwords")

        response = client.post("/simulation/decision", data={
            "action": "choose_strong",
            "scenario_id": "pw_001",
        }, follow_redirects=True)

        assert response.status_code == 200


class TestSimulationImmersiveFlow:
    """Tests de integración para simulaciones inmersivas."""

    @patch("app.ai.analyze_immersive")
    def test_start_immersive_simulation(self, mock_analyze, client, authenticated_user):
        """Test iniciar simulación inmersiva."""
        mock_analyze.return_value = {
            "verdict": "correcto",
            "explanation": "Test",
            "lesson": "Test lesson",
            "points": 100
        }

        response = client.get("/sim/")
        assert response.status_code == 200

        # Iniciar escenario is_001
        response = client.get("/sim/is_001", follow_redirects=True)
        assert response.status_code == 200

    @patch("app.ai.analyze_immersive")
    def test_submit_immersive_decision(self, mock_analyze, client, authenticated_user):
        """Test enviar decisión en simulación inmersiva."""
        mock_analyze.return_value = {
            "verdict": "correcto",
            "explanation": "Test",
            "lesson": "Test lesson",
            "points": 100
        }

        # Iniciar simulación
        client.get("/sim/is_001")

        # Enviar decisión vía JSON
        response = client.post("/sim/decision", json={
            "scenario_id": "is_001",
            "stage_id": "call_intro",
            "choice_id": "hang_up",
        })

        assert response.status_code == 200
        data = response.get_json()
        assert "verdict" in data
        assert "points" in data


class TestQuizFlow:
    """Tests de integración para quiz."""

    @patch("app.services.quiz_service.generate_quiz_questions")
    def test_load_quiz(self, mock_generate, client, authenticated_user):
        """Test cargar quiz."""
        mock_generate.return_value = [
            {
                "id": "ai_001",
                "question": "Test question 1",
                "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
                "correct": "A",
                "explanation": "Explanation 1"
            },
            {
                "id": "ai_002",
                "question": "Test question 2",
                "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
                "correct": "B",
                "explanation": "Explanation 2"
            },
            {
                "id": "ai_003",
                "question": "Test question 3",
                "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
                "correct": "C",
                "explanation": "Explanation 3"
            }
        ]

        response = client.post("/quiz/load", follow_redirects=True)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["total"] == 10

    @patch("app.services.quiz_service.generate_quiz_questions")
    def test_quiz_question_flow(self, mock_generate, client, authenticated_user):
        """Test flujo completo de preguntas del quiz."""
        mock_generate.return_value = [
            {"id": "ai_001", "question": "Q1", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "correct": "A", "explanation": "E1"},
            {"id": "ai_002", "question": "Q2", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "correct": "B", "explanation": "E2"},
            {"id": "ai_003", "question": "Q3", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "correct": "C", "explanation": "E3"}
        ]

        # Cargar quiz
        client.post("/quiz/load")

        # Obtener primera pregunta
        response = client.get("/quiz/question/0")
        assert response.status_code == 200

        # Responder
        response = client.post("/quiz/answer", json={
            "question_id": "q001",  # Primera pregunta fija
            "answer": "B"  # Respuesta correcta para q001
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["is_correct"] is True

    @patch("app.services.quiz_service.generate_quiz_questions")
    def test_quiz_results(self, mock_generate, client, authenticated_user):
        """Test ver resultados del quiz."""
        mock_generate.return_value = [
            {"id": "ai_001", "question": "Q1", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "correct": "A", "explanation": "E1"},
            {"id": "ai_002", "question": "Q2", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "correct": "B", "explanation": "E2"},
            {"id": "ai_003", "question": "Q3", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "correct": "C", "explanation": "E3"}
        ]

        client.post("/quiz/load")

        # Responder todas correctamente (simplificado)
        questions = client.session.get("quiz_questions", [])
        for q in questions:
            client.post("/quiz/answer", json={
                "question_id": q["id"],
                "answer": q["correct"]
            })

        response = client.get("/quiz/results", follow_redirects=True)
        assert response.status_code == 200
        assert b"score" in response.data.lower() or b"resultado" in response.data.lower()