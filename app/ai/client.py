"""
app/ai/client.py
Interfaz común (Protocol) para clientes de IA.
Permite intercambiar proveedores (Gemini, OpenRouter, etc.) sin cambiar el código de negocio.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class AIClient(Protocol):
    """Protocolo que define la interfaz común para todos los clientes de IA."""

    def analyze_phishing(self, scenario: dict, user_action: str) -> dict:
        """Analiza una decisión del usuario en escenario de phishing."""
        ...

    def analyze_password(self, scenario: dict, user_action: str) -> dict:
        """Analiza una decisión del usuario en escenario de contraseñas."""
        ...

    def analyze_immersive(self, scenario: dict, stage: dict, choice: dict, is_correct: bool) -> dict:
        """Analiza una decisión en simulación inmersiva."""
        ...

    def generate_quiz_questions(self, topics_covered: list) -> list:
        """Genera preguntas de quiz con IA."""
        ...

    def chat(self, messages: list, system: str = None) -> str:
        """Chat conversacional libre."""
        ...

    def is_available(self) -> bool:
        """Verifica si el cliente está disponible (API key configurada, etc.)."""
        ...


class AIClientFactory:
    """Factory para crear instancias de clientes de IA."""

    _instance: AIClient | None = None
    _client_class: type[AIClient] | None = None

    @classmethod
    def register(cls, client_class: type[AIClient]) -> None:
        """Registra la clase de cliente a usar."""
        cls._client_class = client_class
        cls._instance = None  # Reset singleton

    @classmethod
    def get_client(cls) -> AIClient:
        """Obtiene la instancia singleton del cliente."""
        if cls._instance is None:
            if cls._client_class is None:
                raise RuntimeError("No AI client registered. Call AIClientFactory.register() first.")
            cls._instance = cls._client_class()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Resetea la instancia (útil para tests)."""
        cls._instance = None