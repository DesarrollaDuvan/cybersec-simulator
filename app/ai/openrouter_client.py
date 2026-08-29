"""
app/ai/openrouter_client.py
Implementación del cliente OpenRouter para CyberTutor IA.
Implementa el protocolo AIClient definido en app.ai.client.
"""

import os
import json
import re
import logging
from typing import Optional

from openai import OpenAI

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

logger = logging.getLogger(__name__)

# Configuración de modelos (orden de prioridad)
PRIMARY_MODEL = "deepseek/deepseek-r1"
FALLBACK_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
ROUTER_MODEL = "openrouter/free"

MODELS = [PRIMARY_MODEL, FALLBACK_MODEL, ROUTER_MODEL]


class OpenRouterClient(AIClient):
    """Cliente OpenRouter implementando la interfaz AIClient."""

    def __init__(self):
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY no configurada")
        
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "CyberTutor IA",
            }
        )

    def is_available(self) -> bool:
        """Verifica si la API key está configurada."""
        api_key = os.environ.get("OPENROUTER_API_KEY")
        return bool(api_key and api_key.strip())

    def _call(self, messages: list, model: str) -> str:
        """Llama a un modelo específico."""
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def _call_with_fallback(self, messages: list) -> tuple[str, str]:
        """Llama probando modelos en orden hasta que uno funcione."""
        for model in MODELS:
            try:
                response = self._call(messages, model)
                return response, model
            except Exception as e:
                err = str(e)
                logger.warning(f"OpenRouter {model} falló: {err[:100]}")
                if "401" in err or "authentication" in err.lower():
                    raise ValueError("API Key de OpenRouter inválida")
                continue
        raise RuntimeError("Ningún modelo disponible")

    def _clean(self, text: str) -> str:
        """Elimina bloques de razonamiento interno que DeepSeek R1 puede incluir."""
        return re.sub(r'<?thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()

    def _generate_json(self, prompt: str) -> dict | list:
        """Genera respuesta JSON probando modelos."""
        messages = [{"role": "user", "content": prompt}]
        response_text, _ = self._call_with_fallback(messages)
        
        # Limpiar posibles backticks de markdown
        raw = response_text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        return json.loads(raw.strip())

    def analyze_phishing(self, scenario: dict, user_action: str) -> dict:
        """Analiza una decisión del usuario en escenario de phishing."""
        if not self.is_available():
            return {
                "analysis": "No se pudo conectar con la IA. Verifica tu OPENROUTER_API_KEY.",
                "tip": "Verifica siempre el dominio del remitente antes de hacer clic.",
                "points": 0,
            }

        prompt = format_phishing_prompt(scenario, user_action, PHISHING_ACTION_LABELS)
        try:
            return self._generate_json(prompt)
        except Exception as e:
            logger.exception("Error en analyze_phishing: %s", e)
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
        except Exception as e:
            logger.exception("Error en analyze_password: %s", e)
            is_correct = user_action == scenario.get("correct_action")
            points = 100 if is_correct else 10
            return {
                "analysis": "No se pudo conectar con la IA en este momento.",
                "tip": "Usa un gestor de contraseñas para crear y guardar contraseñas únicas por cada sitio.",
                "points": points,
            }

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
        except Exception as e:
            logger.exception("Error en analyze_immersive: %s", e)
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
        except Exception as e:
            logger.exception("Error en generate_quiz_questions: %s", e)
            return []

    def chat(self, messages: list, system: str = None) -> str:
        """Chat conversacional libre con fallback de modelos."""
        if not self.is_available():
            return "No se pudo conectar con la IA. Verifica tu OPENROUTER_API_KEY en .env"

        # Preparar mensajes con system prompt
        full_messages = [{"role": "system", "content": system or CHAT_SYSTEM}]
        full_messages.extend(messages)

        try:
            response_text, model_used = self._call_with_fallback(full_messages)
            logger.info(f"OpenRouter chat usando modelo: {model_used}")
            return self._clean(response_text)
        except ValueError as e:
            # Error de autenticación
            return f"❌ {str(e)}"
        except Exception as e:
            logger.exception("Error en chat: %s", e)
            return "No se pudo conectar con ningún modelo en este momento. Intenta de nuevo en unos segundos."