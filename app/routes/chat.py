import os
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from openai import OpenAI
from app.core.offline_ai import generate_offline_response

chat = Blueprint('chat', __name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Eres CyberTutor IA, un asistente experto en ciberseguridad diseñado para 
enseñar y orientar a usuarios sobre protección digital. Tu rol es:

1. Responder preguntas sobre ciberseguridad de forma clara y educativa
2. Explicar conceptos como phishing, malware, ingeniería social, contraseñas seguras, etc.
3. Dar consejos prácticos y accionables adaptados al nivel del usuario
4. Usar ejemplos concretos y situaciones cotidianas para explicar riesgos
5. Motivar al usuario a mejorar sus hábitos de seguridad digital

Responde siempre en español. Sé amigable, educativo y directo. 
Evita tecnicismos innecesarios a menos que el usuario los pida.
Cuando des consejos, hazlos concretos y fáciles de aplicar.
Máximo 3-4 párrafos por respuesta para mantener la conversación fluida."""


@chat.route('/')
@login_required
def chat_view():
    """Página principal del chat."""
    session['chat_history'] = []  # limpiar historial al entrar
    return render_template('chat.html')


@chat.route('/message', methods=['POST'])
@login_required
def send_message():
    """Recibe un mensaje del usuario y retorna la respuesta de Claude."""
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Mensaje vacío'}), 400

    # Recuperar historial de la sesión
    history = session.get('chat_history', [])

    # Agregar mensaje del usuario al historial
    history.append({
        "role": "user",
        "content": user_message
    })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history
            ],
            max_tokens=500
        )

        ai_message = response.choices[0].message.content

        # Agregar respuesta de Claude al historial
        history.append({
            "role": "assistant",
            "content": ai_message
        })

        # Guardar historial en sesión (máx 20 mensajes para no saturar)
        session['chat_history'] = history[-20:]

        return jsonify({
            'response': ai_message,
        })

    except Exception as e:
        ai_message = generate_offline_response(user_message)

        history.append({
            "role": "assistant",
            "content": ai_message
        })

        session['chat_history'] = history[-20:]

        return jsonify({
            'response': ai_message,
            'mode': 'offline'
        })


@chat.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    """Limpia el historial del chat."""
    session['chat_history'] = []
    return jsonify({'status': 'ok'})
