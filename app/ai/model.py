"""
app/ai/model.py — Módulo centralizado de inteligencia artificial.

Todas las llamadas a Claude pasan por aquí.
simulation.py lo importa así:
  from app.ai.model import analyze_with_claude
"""

import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

ACTION_LABELS = {
    "click_link": "Abrió el enlace sospechoso",
    "open_email":  "Abrió el enlace sospechoso",
    "reply":       "Respondió el correo con información",
    "ignore":      "Ignoró y eliminó el correo",
    "report":      "Reportó el correo como phishing",
}


def analyze_with_claude(scenario: dict, user_action: str) -> dict:
    """
    Analiza la decisión del usuario con Claude.

    Parámetros:
      scenario    — dict con keys: sender, subject, body, link, clues, correct_action
      user_action — string: 'click_link' | 'reply' | 'ignore' | 'report'

    Retorna:
      { "analysis": str, "tip": str, "points": int }
    """
    prompt = f"""
Eres CyberTutor IA, experto en ciberseguridad que enseña a identificar phishing.
Un usuario enfrentó este escenario de simulación:

ESCENARIO:
- Remitente: {scenario['sender']}
- Asunto: {scenario['subject']}
- Cuerpo: {scenario['body']}
- Enlace: {scenario.get('link', 'Ninguno')}
- Señales reales de alerta: {', '.join(scenario['clues'])}
- Acción correcta: {scenario['correct_action']}

DECISIÓN DEL USUARIO: {ACTION_LABELS.get(user_action, user_action)}

Responde ÚNICAMENTE con JSON válido, sin markdown ni texto adicional:
{{
  "analysis": "Explicación de 3-4 oraciones sobre si la decisión fue correcta o no, mencionando señales concretas del correo.",
  "tip": "Consejo práctico de 1-2 oraciones para situaciones similares.",
  "points": <entero 0-100>
}}

Puntuación:
- report (cuando era la acción correcta): 100
- report (cuando correct_action era ignore): 90  
- ignore (cuando era la acción correcta): 75
- reply: 25
- click_link u open_email: 0
"""
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
