"""
app/routes/chat.py — integrado con OpenRouter
Modelo: deepseek/deepseek-r1:free  (el más inteligente gratuito)
Fallback: meta-llama/llama-3.3-70b-instruct:free
Fallback 2: openrouter/free (router automático)

OpenRouter es compatible con la API de OpenAI:
    pip install openai

Variable de entorno requerida en .env:
    OPENROUTER_API_KEY=sk-or-v1-...
"""

import os
import re
import traceback
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required

chat = Blueprint('chat', __name__)

# ── Inicializar cliente ──────────────────────────────────────────────────────
_client     = None
_init_error = None

PRIMARY_MODEL  = "deepseek/deepseek-r1"
FALLBACK_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
ROUTER_MODEL   = "openrouter/free"

try:
    from openai import OpenAI
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        _init_error = "OPENROUTER_API_KEY no encontrada en .env"
    else:
        _client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "CyberTutor IA",
            }
        )
        print(f"[chat.py] ✓ OpenRouter listo. Key: {api_key[:14]}...")
except ImportError:
    _init_error = "Librería 'openai' no instalada. Ejecuta: pip install openai"
except Exception as e:
    _init_error = f"Error al inicializar: {str(e)}"

if _init_error:
    print(f"[chat.py] ✗ {_init_error}")


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
No incluyas bloques <think> ni razonamiento interno en tu respuesta."""


def _call(messages: list, model: str) -> str:
    response = _client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def _clean(text: str) -> str:
    """Elimina bloques <think>...</think> que DeepSeek R1 puede incluir."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


# ── Rutas ────────────────────────────────────────────────────────────────────

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

    if _init_error or _client is None:
        return jsonify({'response': f'⚠ Error de configuración: {_init_error}', 'mode': 'error'})

    history  = session.get('chat_history', [])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history
    messages.append({"role": "user", "content": user_message})

    ai_message = None
    model_used = None

    for model in [PRIMARY_MODEL, FALLBACK_MODEL, ROUTER_MODEL]:
        try:
            ai_message = _call(messages, model)
            model_used = model
            break
        except Exception as e:
            err = str(e)
            print(f"[chat.py] {model} falló: {err[:100]}")
            if "401" in err or "authentication" in err.lower():
                return jsonify({
                    'response': '❌ API Key de OpenRouter inválida. Verifica OPENROUTER_API_KEY en tu .env',
                    'mode': 'error'
                })
            continue

    if ai_message is None:
        return jsonify({
            'response': "No se pudo conectar con ningún modelo en este momento. Intenta de nuevo en unos segundos.",
            'mode': 'offline'
        })

    ai_message = _clean(ai_message)

    history.append({"role": "user",      "content": user_message})
    history.append({"role": "assistant", "content": ai_message})
    session['chat_history'] = history[-20:]

    return jsonify({'response': ai_message, 'model_used': model_used})


@chat.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    session['chat_history'] = []
    return jsonify({'status': 'ok'})


@chat.route('/status')
@login_required
def status():
    """Diagnóstico — visita /chat/status en el navegador."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    info = {
        "init_error":      _init_error,
        "client_ready":    _client is not None,
        "api_key_present": bool(api_key),
        "api_key_preview": api_key[:14] + "..." if api_key else "NO ENCONTRADA",
        "primary_model":   PRIMARY_MODEL,
        "fallback_model":  FALLBACK_MODEL,
    }
    if _client:
        try:
            resp = _call([{"role": "user", "content": "Di solo 'OK'."}], PRIMARY_MODEL)
            info["test_call"] = f"✓ {resp[:60]}"
        except Exception as e:
            info["test_call"] = f"✗ {str(e)[:120]}"
    return jsonify(info)
