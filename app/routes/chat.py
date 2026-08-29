"""
app/routes/chat.py — Chat usando la interfaz unificada AIClient (OpenRouter)
Modelo: deepseek/deepseek-r1:free  (el más inteligente gratuito)
Fallback: meta-llama/llama-3.3-70b-instruct:free
Fallback 2: openrouter/free (router automático)

Variable de entorno requerida en .env:
    OPENROUTER_API_KEY=sk-or-v1-...
"""

import logging
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required

from app.ai import chat_openrouter

chat = Blueprint('chat', __name__)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres CyberTutor IA, un asistente experto en ciberseguridad diseñado para 
enseñar y orientar a usuarios sobre protección digital. Tu rol es:

1. Responder preguntas sobre ciberseguridad de forma clara y educativa
2. Explicar conceptos como phishing, malware, ingeniería social, contraseñas seguras, etc.
3. Dar consejos prácticos y accionables adaptados al nivel del usuario
4. Usar ejemplos concretos y situaciones cotidianas para explicar riesgos
5. Motivar al usuario a mejorar sus hábitos de seguridad digital

Responde siempre en español. Sé amigable, educativo y directo.
Evita tecnicismos innecesarios a menos que el usuario los pida.
Máximo 3-4 párrafos por respuesta para mantener la conversación fluida.
No incluyas bloques de razonamiento interno en tu respuesta."""


# ── Rutas ────────────────────────────────────────────────────────────────

@chat.route('/')
@login_required
def chat_view():
    session['chat_history'] = []
    return render_template('chat.html')


@chat.route('/message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Mensaje vacío'}), 400

    history = session.get('chat_history', [])
    messages = history + [{"role": "user", "content": user_message}]

    try:
        ai_message = chat_openrouter(messages, SYSTEM_PROMPT)
    except Exception as e:
        logger.exception("Error en chat: %s", e)
        return jsonify({
            'response': "No se pudo conectar con la IA en este momento. Intenta de nuevo en unos segundos.",
            'mode': 'offline'
        })

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": ai_message})
    session['chat_history'] = history[-20:]

    return jsonify({'response': ai_message})


@chat.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    session['chat_history'] = []
    return jsonify({'status': 'ok'})


@chat.route('/status')
@login_required
def status():
    """Diagnóstico — visita /chat/status en el navegador."""
    import os
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    info = {
        "api_key_present": bool(api_key),
        "api_key_preview": api_key[:14] + "..." if api_key else "NO ENCONTRADA",
    }
    return jsonify(info)