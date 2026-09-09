# app/ai/__init__.py
# Cliente IA centralizado - usa OpenRouterClient por defecto, GeminiClient como alternativa

from app.ai.client import AIClient, AIClientFactory
from app.ai.gemini_client import GeminiClient
from app.ai.openrouter_client import OpenRouterClient

# Registrar OpenRouter como cliente por defecto (usa OPENROUTER_API_KEY del .env)
AIClientFactory.register(OpenRouterClient)

# También registrar Gemini como alternativa (se puede cambiar en runtime)
# AIClientFactory.register(GeminiClient)


def get_ai_client() -> AIClient:
    """Obtiene la instancia singleton del cliente IA configurado."""
    return AIClientFactory.get_client()


def get_openrouter_client() -> AIClient:
    """Obtiene una instancia de OpenRouterClient (para chat)."""
    return OpenRouterClient()


# Funciones de conveniencia para compatibilidad hacia atrás
def analyze_phishing(scenario: dict, user_action: str) -> dict:
    """Analiza decisión de phishing usando el cliente IA activo."""
    return get_ai_client().analyze_phishing(scenario, user_action)


def analyze_password(scenario: dict, user_action: str) -> dict:
    """Analiza decisión de contraseñas usando el cliente IA activo."""
    return get_ai_client().analyze_password(scenario, user_action)


def analyze_immersive(scenario: dict, stage: dict, choice: dict, is_correct: bool) -> dict:
    """Analiza decisión inmersiva usando el cliente IA activo."""
    return get_ai_client().analyze_immersive(scenario, stage, choice, is_correct)


def generate_quiz_questions(topics_covered: list) -> list:
    """Genera preguntas de quiz usando el cliente IA activo."""
    return get_ai_client().generate_quiz_questions(topics_covered)


def chat(messages: list, system: str = None) -> str:
    """Chat conversacional usando el cliente IA activo (OpenRouter por defecto)."""
    return get_ai_client().chat(messages, system)


def chat_openrouter(messages: list, system: str = None) -> str:
    """Chat conversacional usando OpenRouter específicamente."""
    return get_openrouter_client().chat(messages, system)


__all__ = [
    "AIClient",
    "AIClientFactory",
    "GeminiClient",
    "OpenRouterClient",
    "get_ai_client",
    "get_openrouter_client",
    "analyze_phishing",
    "analyze_password",
    "analyze_immersive",
    "generate_quiz_questions",
    "chat",
    "chat_openrouter",
]