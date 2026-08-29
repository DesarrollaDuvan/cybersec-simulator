"""
app/routes/quiz.py — Quiz de ciberseguridad usando QuizService.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required
from app.services import QuizService

quiz = Blueprint('quiz', __name__)


@quiz.route('/')
@login_required
def start():
    return render_template('quiz.html', stage='start')


@quiz.route('/load', methods=['POST'])
@login_required
def load_quiz():
    QuizService.load_quiz()
    questions = session.get('quiz_questions', [])
    return jsonify({'status': 'ok', 'total': len(questions)})


@quiz.route('/question/<int:index>')
@login_required
def get_question(index):
    question = QuizService.get_question(index)
    if not question:
        return redirect(url_for('quiz.start'))
    if index >= len(session.get('quiz_questions', [])):
        return redirect(url_for('quiz.results'))

    return render_template('quiz.html',
        stage='question',
        index=index,
        total=len(session.get('quiz_questions', [])),
        q_id=question['id'],
        question=question['question'],
        options=question['options'],
        ai_generated=question.get('ai_generated', False)
    )


@quiz.route('/question/<int:index>/json')
@login_required
def get_question_json(index):
    question = QuizService.get_question(index)
    if not question:
        return jsonify({'error': 'Pregunta no encontrada'}), 404

    questions = session.get('quiz_questions', [])
    return jsonify({
        'index': index,
        'total': len(questions),
        'id': question['id'],
        'question': question['question'],
        'options': question['options'],
        'ai_generated': question.get('ai_generated', False)
    })


@quiz.route('/answer', methods=['POST'])
@login_required
def submit_answer():
    data = request.get_json()
    q_id = data.get('question_id')
    answer = data.get('answer', '').upper()

    if not q_id:
        return jsonify({'error': 'ID de pregunta requerido'}), 400

    result = QuizService.submit_answer(q_id, answer)

    if 'error' in result:
        return jsonify(result), 404

    return jsonify(result)


@quiz.route('/results')
@login_required
def results():
    result = QuizService.calculate_results()

    if 'error' in result:
        return render_template('quiz.html', stage='start')

    return render_template('quiz.html',
        stage='results',
        score=result['score'],
        correct_count=result['correct_count'],
        total=result['total'],
        level=result['level'],
        level_color=result['level_color'],
        message=result['message'],
        detail=result['detail']
    )