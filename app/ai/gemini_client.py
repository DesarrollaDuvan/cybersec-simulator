"""
app/ai/gemini_client.py
Implementación del cliente Gemini para CyberTutor IA.
Implementa el protocolo AIClient definido en app.ai.client.
"""

import os
import json
import google.generativeai as genai

from app.ai.client import AIClient
from app.ai.prompts import (
    format_phishing_prompt,
    format_password_prompt,
    format_immersive_prompt,
    format_quiz_generation_prompt,
    CHAT_SYSTEM,
)
from app.constants import (
    PHISHING_ACTION_LABELS,
    PASSWORD_ACTION_LABELS,
)


# Configurar la API key una sola vez
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Modelo a usar — gemini-2.0-flash es rápido y gratuito en AI Studio
MODEL_NAME = "gemini-2.0-flash"


class GeminiClient(AIClient):
    """Cliente Gemini implementando la interfaz AIClient."""

    def __init__(self):
        self._model = genai.GenerativeModel(model_name=MODEL_NAME)
        self._json_model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )

    def is_available(self) -> bool:
        """Verifica si la API key está configurada."""
        api_key = os.environ.get("GEMINI_API_KEY")
        return bool(api_key and api_key.strip())

    def _generate_json(self, prompt: str) -> dict | list:
        """Genera respuesta JSON usando el modelo configurado para JSON."""
        response = self._json_model.generate_content(prompt)
        raw = response.text.strip()

        # Limpiar posibles backticks de markdown
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw.strip())

    def _generate_text(self, prompt: str, system: str = None) -> str:
        """Genera respuesta de texto libre."""
        if system:
            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                system_instruction=system
            )
            response = model.generate_content(prompt)
        else:
            response = self._model.generate_content(prompt)
        return response.text.strip()

    def analyze_phishing(self, scenario: dict, user_action: str) -> dict:
        """Analiza una decisión del usuario en escenario de phishing."""
        if not self.is_available():
            return {
                "analysis": "No se pudo conectar con la IA. Verifica tu API key.",
                "tip": "Verifica siempre el dominio del remitente antes de hacer clic.",
                "points": 0,
            }

        prompt = format_phishing_prompt(scenario, user_action, PHISHING_ACTION_LABELS)
        try:
            return self._generate_json(prompt)
        except Exception:
            return {
                "analysis": "No se pudo conectar con la IA en este momento.",
                "tip": "Verifica siempre el dominio del remitente antes de hacer clic.",
                "points": 0,
            }

    def analyze_password(self, scenario: dict, user_action: str) -> dict:
        """Analiza una decisión del usuario en escenario de contraseñas."""
        if not self.is_available():
            is_correct = user_action == scenario.get("correct_action")
            points = 100 if is_correct else 10
            return {
                "analysis": "No se pudo conectar con la IA en este momento.",
                "tip": "Usa un gestor de contraseñas para crear y guardar contraseñas únicas por cada sitio.",
                "points": points,
            }

        prompt = format_password_prompt(scenario, user_action, PASSWORD_ACTION_LABELS)
        try:
            return self._generate_json(prompt)
        except Exception:
            is_correct = user_action == scenario.get("correct_action")
            points = 100 if is_correct else 10
            return {
                "analysis": "No se pudo conectar con la IA en este momento.",
                "tip": "Usa un gestor de contraseñas para crear y guardar contraseñas únicas por cada sitio.",
                "points": points,
            }

    def analyze_phishing_stream(self, scenario: dict, user_action: str):
        """Analiza phishing con streaming (generador de chunks SSE)."""
        if not self.is_available():
            yield f"data: {json.dumps({'type': 'error', 'content': 'No se pudo conectar con la IA. Verifica tu GEMINI_API_KEY.'})}\n\n"
            return

        prompt = format_phishing_prompt(scenario, user_action, PHISHING_ACTION_LABELS)
        try:
            # First get the full response, then stream it character by character
            # (Gemini doesn't support streaming JSON mode easily, so we simulate streaming)
            result = self._generate_json(prompt)
            
            # Stream analysis field
            yield f"data: {json.dumps({'type': 'field', 'field': 'analysis'})}\n\n"
            for char in result.get('analysis', ''):
                yield f"data: {json.dumps({'type': 'chunk', 'content': char})}\n\n"
            
            # Stream tip field
            yield f"data: {json.dumps({'type': 'field', 'field': 'tip'})}\n\n"
            for char in result.get('tip', ''):
                yield f"data: {json.dumps({'type': 'chunk', 'content': char})}\n\n"
            
            # Send points as metadata
            yield f"data: {json.dumps({'type': 'points', 'content': result.get('points', 0)})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': f'Error: {str(e)}'})}\n\n"

    def analyze_password_stream(self, scenario: dict, user_action: str):
        """Analiza contraseñas con streaming (generador de chunks SSE)."""
        if not self.is_available():
            is_correct = user_action == scenario.get("correct_action")
            points = 100 if is_correct else 10
            yield f"data: {json.dumps({'type': 'error', 'content': 'No se pudo conectar con la IA en este momento.'})}\n\n"
            return

        prompt = format_password_prompt(scenario, user_action, PASSWORD_ACTION_LABELS)
        try:
            result = self._generate_json(prompt)
            
            # Stream analysis field
            yield f"data: {json.dumps({'type': 'field', 'field': 'analysis'})}\n\n"
            for char in result.get('analysis', ''):
                yield f"data: {json.dumps({'type': 'chunk', 'content': char})}\n\n"
            
            # Stream tip field
            yield f"data: {json.dumps({'type': 'field', 'field': 'tip'})}\n\n"
            for char in result.get('tip', ''):
                yield f"data: {json.dumps({'type': 'chunk', 'content': char})}\n\n"
            
            # Send points as metadata
            yield f"data: {json.dumps({'type': 'points', 'content': result.get('points', 0)})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': f'Error: {str(e)}'})}\n\n"

    def analyze_immersive(self, scenario: dict, stage: dict, choice: dict, is_correct: bool) -> dict:
        """Analiza una decisión en simulación inmersiva."""
        if not self.is_available():
            return {
                "verdict": "correcto" if is_correct else "incorrecto",
                "explanation": stage.get("consequence_good" if is_correct else "consequence_bad", ""),
                "lesson": "Siempre verifica antes de actuar.",
                "points": 100 if is_correct else 0,
            }

        prompt = format_immersive_prompt(scenario, stage, choice, is_correct)
        try:
            return self._generate_json(prompt)
        except Exception:
            return {
                "verdict": "correcto" if is_correct else "incorrecto",
                "explanation": stage.get("consequence_good" if is_correct else "consequence_bad", ""),
                "lesson": "Piensa antes de actuar.",
                "points": 100 if is_correct else 0,
            }

    def generate_quiz_questions(self, topics_covered: list) -> list:
        """Genera preguntas de quiz con IA."""
        if not self.is_available():
            return []

        prompt = format_quiz_generation_prompt(topics_covered)
        try:
            questions = self._generate_json(prompt)
            for i, q in enumerate(questions):
                q["id"] = f"ai_{i+1:03d}"
            return questions
        except Exception:
            return []

    def chat(self, messages: list, system: str = None) -> str:
        """Chat conversacional libre."""
        if not self.is_available():
            return "No se pudo conectar con la IA. Verifica tu GEMINI_API_KEY en .env"

        # Convertir historial al formato de Gemini
        gemini_history = []
        for msg in messages[:-1]:  # Excluir el último mensaje que es el prompt actual
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({
                "role": role,
                "parts": [msg["content"]]
            })

        current_prompt = messages[-1]["content"] if messages else ""
        system_prompt = system or CHAT_SYSTEM

        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_prompt
        )

        if gemini_history:
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(current_prompt)
        else:
            response = model.generate_content(current_prompt)

        # Limpiar bloques de razonamiento interno (DeepSeek style)
        text = response.text.strip()
        import re
        text = re.sub(r'<?thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        text = re.sub(r'<?reasoning>.*?</reasoning>', '', text, flags=re.DOTALL)
        return text.strip()


# Funciones de compatibilidad hacia atrás (deprecated)
def ask_gemini(prompt: str, system: str = None, history: list = None) -> str:
    """@deprecated Usa GeminiClient().chat() en su lugar."""
    client = GeminiClient()
    messages = []
    if history:
        for msg in history:
            role = "assistant" if msg["role"] == "model" else "user"
            messages.append({"role": role, "content": msg["parts"][0]})
    messages.append({"role": "user", "content": prompt})
    return client.chat(messages, system)


def ask_gemini_json(prompt: str) -> dict | list:
    """@deprecated Usa GeminiClient()._generate_json() en su lugar."""
    client = GeminiClient()
    return client._generate_json(prompt)


def history_to_gemini(flask_history: list) -> list:
    """Convierte el historial de Flask al formato Gemini."""
    gemini_history = []
    for msg in flask_history:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({
            "role": role,
            "parts": [msg["content"]]
        })
    return gemini_history