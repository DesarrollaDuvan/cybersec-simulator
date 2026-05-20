"""
app/routes/quiz.py — migrado de Claude a Gemini
"""

import json
import random
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from app.ai.gemini_client import ask_gemini_json
from app.models.progress import QuizResult
from app import db

quiz = Blueprint('quiz', __name__)

# ── Banco de preguntas ───────────────────────────────────────────────────────

QUESTION_BANK = [
    {
        "id": "q001",
        "question": "¿Cuál de las siguientes es la señal MÁS clara de un correo de phishing?",
        "options": {"A": "El correo tiene imágenes y logos de una empresa conocida", "B": "El enlace lleva a un dominio diferente al de la empresa real", "C": "El correo fue enviado un domingo", "D": "El correo pide que respondas antes de una semana"},
        "correct": "B",
        "explanation": "Los atacantes usan dominios falsos (ej: banco-seguro.net en lugar de banco.com.co). Siempre verifica la URL antes de hacer clic."
    },
    {
        "id": "q002",
        "question": "¿Qué hace que una contraseña sea considerada segura?",
        "options": {"A": "Usar tu fecha de nacimiento seguida de un símbolo", "B": "Tener mínimo 8 caracteres con solo letras", "C": "Combinar letras mayúsculas, minúsculas, números y símbolos con más de 12 caracteres", "D": "Usar el nombre de tu mascota en mayúsculas"},
        "correct": "C",
        "explanation": "Una contraseña segura debe tener al menos 12 caracteres y combinar los 4 tipos de caracteres. Evita información personal predecible."
    },
    {
        "id": "q003",
        "question": "Recibes un correo de tu 'banco' pidiendo que confirmes tus datos urgentemente. ¿Qué haces?",
        "options": {"A": "Haces clic en el enlace y actualizas tus datos", "B": "Respondes el correo con tus datos para ser más rápido", "C": "Llamas directamente al banco usando el número oficial de su sitio web", "D": "Reenvías el correo a tus contactos para advertirles"},
        "correct": "C",
        "explanation": "Nunca uses los enlaces o teléfonos de un correo sospechoso. Siempre contacta al banco por sus canales oficiales verificados."
    },
    {
        "id": "q004",
        "question": "¿Qué es la ingeniería social en ciberseguridad?",
        "options": {"A": "Un tipo de antivirus para redes empresariales", "B": "Manipular psicológicamente a personas para obtener información confidencial", "C": "Un método para construir contraseñas más complejas", "D": "Un protocolo de seguridad para redes WiFi"},
        "correct": "B",
        "explanation": "La ingeniería social explota la psicología humana (urgencia, miedo, confianza) para engañar a las personas y obtener acceso o información."
    },
    {
        "id": "q005",
        "question": "¿Cuál de estas prácticas es MÁS segura para gestionar contraseñas?",
        "options": {"A": "Usar la misma contraseña fuerte en todos los sitios", "B": "Escribir las contraseñas en un cuaderno bajo llave", "C": "Usar un gestor de contraseñas confiable", "D": "Cambiar todas las contraseñas cada semana"},
        "correct": "C",
        "explanation": "Un gestor de contraseñas genera y almacena contraseñas únicas y complejas para cada sitio, sin que tengas que memorizarlas."
    },
    {
        "id": "q006",
        "question": "¿Qué significa que un sitio web tiene 'HTTPS' en su URL?",
        "options": {"A": "El sitio fue verificado por el gobierno", "B": "La comunicación entre tu navegador y el sitio está cifrada", "C": "El sitio es 100% seguro y no puede ser falso", "D": "El sitio tiene un antivirus instalado"},
        "correct": "B",
        "explanation": "HTTPS cifra los datos en tránsito, pero NO garantiza que el sitio sea legítimo. Un sitio de phishing también puede usar HTTPS."
    },
    {
        "id": "q007",
        "question": "¿Qué es el ransomware?",
        "options": {"A": "Un programa que mejora la velocidad de tu computador", "B": "Un virus que muestra anuncios no deseados", "C": "Malware que cifra tus archivos y exige un pago para recuperarlos", "D": "Una herramienta de monitoreo de redes"},
        "correct": "C",
        "explanation": "El ransomware secuestra tus archivos cifrándolos. La mejor protección es tener copias de seguridad actualizadas y no abrir archivos sospechosos."
    },
    {
        "id": "q008",
        "question": "Estás en una cafetería y necesitas hacer una transacción bancaria. ¿Qué haces?",
        "options": {"A": "Te conectas al WiFi gratuito del local sin problema", "B": "Usas los datos móviles de tu celular o una VPN", "C": "Pides la contraseña del WiFi al administrador para mayor seguridad", "D": "Esperas a llegar a casa, pero si es urgente usas el WiFi público"},
        "correct": "B",
        "explanation": "Las redes WiFi públicas pueden ser interceptadas. Para transacciones sensibles usa tus datos móviles o una VPN confiable."
    },
    {
        "id": "q009",
        "question": "¿Qué es la autenticación de dos factores (2FA)?",
        "options": {"A": "Tener dos contraseñas diferentes para la misma cuenta", "B": "Un segundo paso de verificación además de la contraseña (ej: código por SMS)", "C": "Iniciar sesión desde dos dispositivos al mismo tiempo", "D": "Una contraseña con dos tipos de caracteres"},
        "correct": "B",
        "explanation": "El 2FA agrega una capa extra de seguridad. Aunque alguien robe tu contraseña, necesitará también el segundo factor para entrar."
    },
    {
        "id": "q010",
        "question": "Recibes un USB en el piso de tu empresa sin identificación. ¿Qué haces?",
        "options": {"A": "Lo conectas para ver qué contiene y reportarlo", "B": "Lo entregas al departamento de TI sin conectarlo a ningún equipo", "C": "Lo conectas en un computador personal, no en el de trabajo", "D": "Lo formateas antes de usarlo"},
        "correct": "B",
        "explanation": "Los USB abandonados pueden contener malware que se ejecuta automáticamente al conectarse. Nunca los conectes — entrégalos a TI."
    },
    {
        "id": "q011",
        "question": "¿Cuál de los siguientes es un ejemplo de ataque de 'vishing'?",
        "options": {"A": "Un correo falso que imita a tu banco", "B": "Una llamada telefónica de alguien que dice ser del soporte técnico de Microsoft", "C": "Un mensaje de texto con un enlace sospechoso", "D": "Una página web falsa que imita a PayPal"},
        "correct": "B",
        "explanation": "El vishing usa llamadas telefónicas para engañar. Microsoft o tu banco nunca te llamarán para pedirte acceso a tu equipo."
    },
    {
        "id": "q012",
        "question": "¿Con qué frecuencia deberías hacer copias de seguridad de tus datos importantes?",
        "options": {"A": "Una vez al año es suficiente", "B": "Solo cuando vayas a formatear el computador", "C": "Regularmente, idealmente de forma automática y en múltiples ubicaciones", "D": "Solo si trabajas con información muy confidencial"},
        "correct": "C",
        "explanation": "La regla 3-2-1: 3 copias, en 2 medios diferentes, con 1 copia fuera de sitio. Las copias regulares te protegen del ransomware."
    },
    {
        "id": "q013",
        "question": "¿Qué debes hacer PRIMERO si crees que tu cuenta fue hackeada?",
        "options": {"A": "Esperar a ver si pasa algo antes de actuar", "B": "Cambiar la contraseña desde un dispositivo seguro y activar 2FA", "C": "Eliminar la cuenta y crear una nueva", "D": "Publicar en redes sociales para advertir a tus contactos"},
        "correct": "B",
        "explanation": "Actúa inmediatamente: cambia la contraseña desde un dispositivo limpio, activa 2FA y revisa la actividad reciente de la cuenta."
    },
    {
        "id": "q014",
        "question": "¿Cuál es el objetivo principal del 'smishing'?",
        "options": {"A": "Infectar tu computador con un virus por correo", "B": "Engañarte mediante mensajes de texto para robar información o instalar malware", "C": "Hackear tu WiFi doméstico", "D": "Acceder a tu cámara web sin permiso"},
        "correct": "B",
        "explanation": "El smishing usa SMS falsos. Desconfía de mensajes con enlaces urgentes de remitentes desconocidos."
    },
    {
        "id": "q015",
        "question": "¿Qué significa 'actualizar el software' desde el punto de vista de la seguridad?",
        "options": {"A": "Agregar nuevas funciones para mejorar la experiencia", "B": "Corregir vulnerabilidades que los atacantes podrían explotar", "C": "Hacer el programa más lento para mayor seguridad", "D": "Cambiar la interfaz visual del programa"},
        "correct": "B",
        "explanation": "Las actualizaciones parchean vulnerabilidades conocidas. Mantener el software actualizado es una de las defensas más importantes."
    },
]


# ── Generación de preguntas con Gemini ───────────────────────────────────────

def generate_ai_questions(topics_covered: list) -> list:
    prompt = f"""Eres un experto en ciberseguridad creando un quiz educativo en español.
Ya se cubrieron estos temas: {', '.join(topics_covered)}.

Genera exactamente 3 preguntas NUEVAS de selección múltiple sobre ciberseguridad,
enfocadas en temas cotidianos y prácticos para usuarios no técnicos.

Responde ÚNICAMENTE con un array JSON válido, sin markdown ni texto extra:
[
  {{
    "id": "ai_001",
    "question": "texto de la pregunta",
    "options": {{"A": "opción A", "B": "opción B", "C": "opción C", "D": "opción D"}},
    "correct": "letra correcta (A, B, C o D)",
    "explanation": "explicación breve (2 oraciones)"
  }},
  {{...}},
  {{...}}
]

Reglas:
- Preguntas prácticas y aplicables al día a día
- Una sola respuesta correcta por pregunta
- Nivel de dificultad: intermedio
- Temas sugeridos: privacidad en redes sociales, apps maliciosas, seguridad móvil,
  deepfakes, datos personales, videollamadas seguras, actualizaciones de seguridad
"""
    try:
        questions = ask_gemini_json(prompt)
        for i, q in enumerate(questions):
            q["id"] = f"ai_{i+1:03d}"
        return questions
    except Exception:
        # Fallback: preguntas adicionales del banco
        return []


# ── Rutas ────────────────────────────────────────────────────────────────────

@quiz.route('/')
@login_required
def start():
    return render_template('quiz.html', stage='start')


@quiz.route('/load', methods=['POST'])
@login_required
def load_quiz():
    fixed = random.sample(QUESTION_BANK, 7)
    topics = [q["question"][:40] for q in fixed]

    ai_questions = generate_ai_questions(topics)

    # Fallback si Gemini falla
    if len(ai_questions) < 3:
        remaining = [q for q in QUESTION_BANK if q not in fixed]
        ai_questions = random.sample(remaining, min(3, len(remaining)))

    all_questions = fixed + ai_questions
    for q in ai_questions:
        q["ai_generated"] = True

    session['quiz_questions'] = all_questions
    session['quiz_answers']   = {}
    session['quiz_current']   = 0

    return jsonify({'status': 'ok', 'total': len(all_questions)})


@quiz.route('/question/<int:index>')
@login_required
def get_question(index):
    questions = session.get('quiz_questions', [])
    if not questions:
        return redirect(url_for('quiz.start'))
    if index >= len(questions):
        return redirect(url_for('quiz.results'))

    q = questions[index]
    return render_template('quiz.html',
        stage='question',
        index=index,
        total=len(questions),
        q_id=q['id'],
        question=q['question'],
        options=q['options'],
        ai_generated=q.get('ai_generated', False)
    )


@quiz.route('/question/<int:index>/json')
@login_required
def get_question_json(index):
    questions = session.get('quiz_questions', [])
    if not questions or index >= len(questions):
        return jsonify({'error': 'Pregunta no encontrada'}), 404
    q = questions[index]
    return jsonify({
        'index': index, 'total': len(questions),
        'id': q['id'], 'question': q['question'],
        'options': q['options'], 'ai_generated': q.get('ai_generated', False)
    })


@quiz.route('/answer', methods=['POST'])
@login_required
def submit_answer():
    data     = request.get_json()
    q_id     = data.get('question_id')
    answer   = data.get('answer', '').upper()
    questions = session.get('quiz_questions', [])
    question  = next((q for q in questions if q['id'] == q_id), None)

    if not question:
        return jsonify({'error': 'Pregunta no encontrada'}), 404

    correct    = question['correct']
    is_correct = answer == correct

    answers = session.get('quiz_answers', {})
    answers[q_id] = {'given': answer, 'correct': correct, 'is_correct': is_correct}
    session['quiz_answers'] = answers

    return jsonify({
        'is_correct':   is_correct,
        'correct_answer': correct,
        'explanation':  question['explanation'],
        'correct_text': question['options'].get(correct, '')
    })


@quiz.route('/results')
@login_required
def results():
    questions = session.get('quiz_questions', [])
    answers   = session.get('quiz_answers',   {})

    if not questions:
        return render_template('quiz.html', stage='start')

    total         = len(questions)
    correct_count = sum(1 for a in answers.values() if a['is_correct'])
    score         = round((correct_count / total) * 100)

    if score >= 90:
        level, level_color = "Experto",      "green"
        message = "¡Excelente! Tienes un dominio sólido de la ciberseguridad."
    elif score >= 70:
        level, level_color = "Avanzado",     "blue"
        message = "Muy bien. Conoces los conceptos clave, sigue practicando."
    elif score >= 50:
        level, level_color = "Intermedio",   "yellow"
        message = "Vas por buen camino. Te recomendamos repasar los temas fallidos."
    else:
        level, level_color = "Principiante", "red"
        message = "Hay oportunidad de mejorar. Revisa los módulos del dashboard."

    # Guardar en BD
    try:
        record = QuizResult(
            user_id=current_user.id,
            score=score,
            correct=correct_count,
            total=total
        )
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()

    detail = []
    for q in questions:
        ans = answers.get(q['id'], {})
        detail.append({
            'question':     q['question'],
            'given':        ans.get('given', '—'),
            'correct':      q['correct'],
            'correct_text': q['options'].get(q['correct'], ''),
            'is_correct':   ans.get('is_correct', False),
            'explanation':  q['explanation'],
            'ai_generated': q.get('ai_generated', False)
        })

    return render_template('quiz.html',
        stage='results', score=score,
        correct_count=correct_count, total=total,
        level=level, level_color=level_color,
        message=message, detail=detail
    )
