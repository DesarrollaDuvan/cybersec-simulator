# tests/unit/test_ai_clients.py
import pytest
from unittest.mock import patch, MagicMock

from app.ai.gemini_client import GeminiClient
from app.ai.client import AIClientFactory


class TestGeminiClient:
    """Tests para GeminiClient."""

    def test_is_available_without_key(self, app):
        """Test que is_available retorna False sin API key."""
        with app.app_context():
            import os
            original_key = os.environ.get("GEMINI_API_KEY")
            os.environ["GEMINI_API_KEY"] = ""
            try:
                client = GeminiClient()
                assert client.is_available() is False
            finally:
                if original_key:
                    os.environ["GEMINI_API_KEY"] = original_key
                else:
                    os.environ.pop("GEMINI_API_KEY", None)

    @patch("app.ai.gemini_client.genai")
    def test_analyze_phishing_fallback(self, mock_genai, app):
        """Test fallback cuando IA falla."""
        with app.app_context():
            client = GeminiClient()

            # Simular error en IA
            mock_genai.GenerativeModel.return_value.generate_content.side_effect = Exception("API Error")

            scenario = {
                "sender": "test@test.com",
                "subject": "Test",
                "body": "Test body",
                "clues": ["clue1"],
                "correct_action": "report"
            }

            result = client.analyze_phishing(scenario, "report")

            assert "analysis" in result
            assert "tip" in result
            assert "points" in result
            assert result["points"] == 0  # Fallback points

    @patch("app.ai.gemini_client.genai")
    def test_analyze_password_fallback(self, mock_genai, app):
        """Test fallback para análisis de contraseñas."""
        with app.app_context():
            client = GeminiClient()

            mock_genai.GenerativeModel.return_value.generate_content.side_effect = Exception("API Error")

            scenario = {
                "title": "Test",
                "context": "Test context",
                "clues": ["clue1"],
                "correct_action": "choose_strong"
            }

            result = client.analyze_password(scenario, "choose_strong")

            assert "analysis" in result
            assert "tip" in result
            assert "points" in result
            assert result["points"] == 100  # Correct action = 100 points fallback

    @patch("app.ai.gemini_client.genai")
    def test_analyze_immersive_fallback(self, mock_genai, app):
        """Test fallback para simulación inmersiva."""
        with app.app_context():
            client = GeminiClient()

            mock_genai.GenerativeModel.return_value.generate_content.side_effect = Exception("API Error")

            scenario = {"title": "Test Scenario"}
            stage = {
                "id": "stage1",
                "consequence_good": "Good",
                "consequence_bad": "Bad"
            }
            choice = {"id": "choice1", "label": "Choice 1"}

            result = client.analyze_immersive(scenario, stage, choice, True)

            assert result["verdict"] == "correcto"
            assert result["points"] == 100

    @patch("app.ai.gemini_client.genai")
    def test_generate_quiz_questions_fallback(self, mock_genai, app):
        """Test fallback para generación de quiz."""
        with app.app_context():
            client = GeminiClient()

            mock_genai.GenerativeModel.return_value.generate_content.side_effect = Exception("API Error")

            result = client.generate_quiz_questions(["phishing"])
            assert result == []


class TestAIClientFactory:
    """Tests para AIClientFactory."""

    def test_register_and_get_client(self, app):
        """Test registro y obtención de cliente."""
        with app.app_context():
            # Resetear factory
            AIClientFactory.reset()

            # Registrar cliente mock
            class MockClient:
                def is_available(self): return True
                def analyze_phishing(self, s, a): return {}
                def analyze_password(self, s, a): return {}
                def analyze_immersive(self, s, st, c, ic): return {}
                def generate_quiz_questions(self, t): return []
                def chat(self, m, s=None): return ""

            AIClientFactory.register(MockClient)
            client = AIClientFactory.get_client()

            assert isinstance(client, MockClient)
            assert client.is_available() is True

    def test_get_client_without_register(self, app):
        """Test error al obtener cliente sin registrar."""
        with app.app_context():
            AIClientFactory.reset()
            with pytest.raises(RuntimeError):
                AIClientFactory.get_client()