# tests/unit/test_quiz_service.py
import pytest
from unittest.mock import patch

from app.services.quiz_service import QuizService


class TestQuizService:
    """Tests para QuizService."""

    def test_question_bank_size(self):
        """Test que el banco de preguntas tiene 15 preguntas."""
        assert len(QuizService.QUESTION_BANK) == 15

    def test_question_structure(self):
        """Test que cada pregunta tiene la estructura correcta."""
        for q in QuizService.QUESTION_BANK:
            assert "id" in q
            assert "question" in q
            assert "options" in q
            assert "correct" in q
            assert "explanation" in q
            assert q["correct"] in ["A", "B", "C", "D"]
            assert set(q["options"].keys()) == {"A", "B", "C", "D"}

    def test_load_quiz(self, app, authenticated_user, client):
        """Test cargar quiz completo."""
        with app.app_context():
            questions = QuizService.load_quiz()
            assert len(questions) == 10  # 7 fijas + 3 IA (o fallback)
            assert "quiz_questions" in session
            assert len(session["quiz_questions"]) == 10

    def test_get_question(self, app, authenticated_user, client):
        """Test obtener pregunta por índice."""
        with app.app_context():
            QuizService.load_quiz()
            q = QuizService.get_question(0)
            assert q is not None
            assert "id" in q

            # Índice fuera de rango
            q = QuizService.get_question(999)
            assert q is None

    def test_submit_answer_correct(self, app, authenticated_user, client):
        """Test enviar respuesta correcta."""
        with app.app_context():
            QuizService.load_quiz()
            questions = session.get("quiz_questions", [])
            first_q = questions[0]
            correct_answer = first_q["correct"]

            result = QuizService.submit_answer(first_q["id"], correct_answer)

            assert result["is_correct"] is True
            assert result["correct_answer"] == correct_answer

    def test_submit_answer_incorrect(self, app, authenticated_user, client):
        """Test enviar respuesta incorrecta."""
        with app.app_context():
            QuizService.load_quiz()
            questions = session.get("quiz_questions", [])
            first_q = questions[0]
            # Respuesta incorrecta (diferente a la correcta)
            wrong_answer = "A" if first_q["correct"] != "A" else "B"

            result = QuizService.submit_answer(first_q["id"], wrong_answer)

            assert result["is_correct"] is False

    def test_calculate_results(self, app, authenticated_user, client):
        """Test calcular resultados finales."""
        with app.app_context():
            QuizService.load_quiz()
            questions = session.get("quiz_questions", [])

            # Responder todas correctamente
            for q in questions:
                QuizService.submit_answer(q["id"], q["correct"])

            result = QuizService.calculate_results()

            assert result["score"] == 100
            assert result["correct_count"] == 10
            assert result["total"] == 10
            assert result["level"] == "Experto"

    @patch("app.services.quiz_service.generate_quiz_questions")
    def test_generate_ai_questions_mock(self, mock_generate, app, authenticated_user, client):
        """Test generación de preguntas con IA mockeada."""
        mock_generate.return_value = [
            {
                "id": "ai_001",
                "question": "Pregunta de prueba 1",
                "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
                "correct": "A",
                "explanation": "Explicación 1"
            },
            {
                "id": "ai_002",
                "question": "Pregunta de prueba 2",
                "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
                "correct": "B",
                "explanation": "Explicación 2"
            },
            {
                "id": "ai_003",
                "question": "Pregunta de prueba 3",
                "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
                "correct": "C",
                "explanation": "Explicación 3"
            }
        ]

        with app.app_context():
            questions = QuizService.generate_ai_questions(["phishing", "passwords"])
            assert len(questions) == 3
            assert all(q.get("ai_generated") is not False for q in questions)