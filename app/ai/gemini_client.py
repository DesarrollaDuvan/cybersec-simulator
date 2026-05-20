"""
app/ai/gemini_client.py
Cliente centralizado de Google Gemini para CyberTutor IA.

Todos los módulos (chat, simulation, quiz) importan desde aquí:
    from app.ai.gemini_client import ask_gemini, ask_gemini_json

Instala la dependencia:
    pip install google-generativeai

Variable de entorno requerida en .env:
    GEMINI_API_KEY=AIza...
"""

import os
import json
import google.generativeai as genai

# Configurar la API key una sola vez
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Modelo a usar — gemini-2.0-flash es rápido y gratuito en AI Studio
MODEL_NAME = "gemini-2.0-flash"


def ask_gemini(prompt: str, system: str = None, history: list = None) -> str:
    """
    Llamada simple a Gemini. Retorna el texto de la respuesta.

    Parámetros:
      prompt  — mensaje del usuario
      system  — instrucciones de sistema (opcional)
      history — lista de mensajes previos en formato
                [{"role": "user"|"model", "parts": ["texto"]}]
    """
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system or ""
    )

    if history:
        chat = model.start_chat(history=history)
        response = chat.send_message(prompt)
    else:
        response = model.generate_content(prompt)

    return response.text.strip()


def ask_gemini_json(prompt: str) -> dict | list:
    """
    Llamada a Gemini esperando respuesta JSON.
    Limpia los backticks de markdown automáticamente.
    Lanza json.JSONDecodeError si la respuesta no es JSON válido.
    """
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={"response_mime_type": "application/json"}
    )
    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Limpiar posibles backticks
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())


def history_to_gemini(flask_history: list) -> list:
    """
    Convierte el historial de Flask (formato OpenAI/Anthropic)
    al formato que espera Gemini:
      [{"role": "user"|"model", "parts": ["texto"]}]
    """
    gemini_history = []
    for msg in flask_history:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({
            "role": role,
            "parts": [msg["content"]]
        })
    return gemini_history
