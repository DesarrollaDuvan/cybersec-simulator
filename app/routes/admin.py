from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.progress import QuizResult, SimulationResult, CourseVisit

admin = Blueprint('admin', __name__)


# ── Decorador de protección admin ──────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso restringido al panel de administrador.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated


# ── Helpers ────────────────────────────────────────────────────────────────

def get_global_stats():
    """Calcula métricas globales para el dashboard."""
    total_users        = User.query.filter_by(is_admin=False).count()
    active_users       = User.query.filter_by(is_admin=False, is_active=True).count()
    total_quiz         = QuizResult.query.count()
    total_simulations  = SimulationResult.query.count()

    avg_score = db.session.query(func.avg(QuizResult.score)).scalar()
    avg_score = round(avg_score) if avg_score else 0

    correct_sims = SimulationResult.query.filter_by(is_correct=True).count()
    sim_rate = round((correct_sims / total_simulations * 100) if total_simulations else 0)

    # Nuevos usuarios últimos 7 días
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(
        User.created_at >= week_ago,
        User.is_admin == False
    ).count()

    # Actividad últimos 7 días
    quiz_week = QuizResult.query.filter(QuizResult.created_at >= week_ago).count()
    sim_week  = SimulationResult.query.filter(SimulationResult.created_at >= week_ago).count()

    # Top performers (top 5 por mejor score en quiz)
    top_users = db.session.query(
        User,
        func.max(QuizResult.score).label('best_score'),
        func.count(QuizResult.id).label('quiz_count')
    ).join(QuizResult).filter(User.is_admin == False)\
     .group_by(User.id)\
     .order_by(func.max(QuizResult.score).desc())\
     .limit(5).all()

    # Distribución de puntajes
    score_dist = {
        'experto':     QuizResult.query.filter(QuizResult.score >= 90).count(),
        'avanzado':    QuizResult.query.filter(QuizResult.score >= 70, QuizResult.score < 90).count(),
        'intermedio':  QuizResult.query.filter(QuizResult.score >= 50, QuizResult.score < 70).count(),
        'principiante':QuizResult.query.filter(QuizResult.score < 50).count(),
    }

    # Cursos más visitados
    course_visits = db.session.query(
        CourseVisit.course_id,
        func.count(CourseVisit.id).label('visits')
    ).group_by(CourseVisit.course_id)\
     .order_by(func.count(CourseVisit.id).desc()).all()

    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_quiz': total_quiz,
        'total_simulations': total_simulations,
        'avg_score': avg_score,
        'sim_rate': sim_rate,
        'new_users_week': new_users_week,
        'quiz_week': quiz_week,
        'sim_week': sim_week,
        'top_users': top_users,
        'score_dist': score_dist,
        'course_visits': course_visits,
    }


# ── RUTAS ─────────────────────────────────────────────────────────────────

@admin.route('/')
@login_required
@admin_required
def dashboard():
    """Dashboard principal con métricas globales."""
    stats = get_global_stats()
    return render_template('admin/dashboard_admin.html', stats=stats)


# ── CRUD USUARIOS ──────────────────────────────────────────────────────────

@admin.route('/users')
@login_required
@admin_required
def users():
    """Lista paginada de usuarios con búsqueda."""
    search = request.args.get('q', '').strip()
    page   = request.args.get('page', 1, type=int)

    query = User.query.filter_by(is_admin=False)
    if search:
        query = query.filter(User.email.ilike(f'%{search}%') | User.name.ilike(f'%{search}%'))

    users_paginated = query.order_by(User.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/users_admin.html', users=users_paginated, search=search)


@admin.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Crear un nuevo usuario manualmente."""
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        name     = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        is_admin = bool(request.form.get('is_admin'))

        if not email or not password:
            flash('Email y contraseña son obligatorios.', 'error')
            return render_template('admin/user_form.html', action='create', user=None)

        if User.query.filter_by(email=email).first():
            flash('Ya existe un usuario con ese correo.', 'error')
            return render_template('admin/user_form.html', action='create', user=None)

        user = User(
            email=email,
            name=name,
            password=generate_password_hash(password),
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Usuario {email} creado correctamente.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', action='create', user=None)


@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Editar datos de un usuario."""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name     = request.form.get('name', '').strip()
        user.email    = request.form.get('email', '').strip()
        user.is_active = bool(request.form.get('is_active'))

        new_password = request.form.get('password', '').strip()
        if new_password:
            user.password = generate_password_hash(new_password)

        db.session.commit()
        flash(f'Usuario {user.email} actualizado.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', action='edit', user=user)


@admin.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """Activar / desactivar un usuario."""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activado' if user.is_active else 'desactivado'
    return jsonify({'status': 'ok', 'is_active': user.is_active, 'message': f'Usuario {status}'})


@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Eliminar un usuario y todo su historial."""
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        return jsonify({'error': 'No puedes eliminar un administrador'}), 403
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario eliminado correctamente.', 'success')
    return jsonify({'status': 'ok'})


@admin.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    """Resetear la contraseña de un usuario."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_password = data.get('password', '').strip()

    if len(new_password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'Contraseña actualizada'})


# ── DETALLE DE PROGRESO ────────────────────────────────────────────────────

@admin.route('/users/<int:user_id>/progress')
@login_required
@admin_required
def user_progress(user_id):
    """Vista detallada del progreso de un usuario."""
    user = User.query.get_or_404(user_id)

    quiz_results = QuizResult.query.filter_by(user_id=user_id)\
                    .order_by(QuizResult.created_at.desc()).all()

    sim_results = SimulationResult.query.filter_by(user_id=user_id)\
                    .order_by(SimulationResult.created_at.desc()).all()

    course_visits = CourseVisit.query.filter_by(user_id=user_id)\
                    .order_by(CourseVisit.visited_at.desc()).all()

    # Evolución de scores en quiz (para gráfica)
    quiz_history = [
        {'date': r.created_at.strftime('%d/%m'), 'score': r.score}
        for r in reversed(quiz_results[:10])
    ]

    return render_template('admin/user_progress.html',
        user=user,
        quiz_results=quiz_results,
        sim_results=sim_results,
        course_visits=course_visits,
        quiz_history=quiz_history,
    )


# ── API RÁPIDA PARA GRÁFICAS ───────────────────────────────────────────────

@admin.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """Endpoint JSON para refrescar estadísticas en tiempo real."""
    stats = get_global_stats()
    return jsonify({
        'total_users':    stats['total_users'],
        'total_quiz':     stats['total_quiz'],
        'avg_score':      stats['avg_score'],
        'sim_rate':       stats['sim_rate'],
        'score_dist':     stats['score_dist'],
    })
