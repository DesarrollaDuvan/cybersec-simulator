from app import db
from flask_login import UserMixin
from datetime import datetime
from app import db
from flask_login import UserMixin

 
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id           = db.Column(db.Integer, primary_key=True)
    email        = db.Column(db.String(100), unique=True, nullable=False)
    password     = db.Column(db.String(255), nullable=False)
    name         = db.Column(db.String(100), default='')
    is_admin     = db.Column(db.Boolean, default=False)
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    last_login   = db.Column(db.DateTime, nullable=True)

    # Relaciones
    quiz_results       = db.relationship('QuizResult',       backref='user', lazy=True, cascade='all, delete-orphan')
    simulation_results = db.relationship('SimulationResult', backref='user', lazy=True, cascade='all, delete-orphan')
    course_visits      = db.relationship('CourseVisit',      backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    # ── Propiedades de resumen para el dashboard ──

    @property
    def quiz_count(self):
        return len(self.quiz_results)

    @property
    def avg_quiz_score(self):
        if not self.quiz_results:
            return 0
        return round(sum(r.score for r in self.quiz_results) / len(self.quiz_results))

    @property
    def best_quiz_score(self):
        if not self.quiz_results:
            return 0
        return max(r.score for r in self.quiz_results)

    @property
    def simulation_count(self):
        return len(self.simulation_results)

    @property
    def simulation_correct(self):
        return sum(1 for r in self.simulation_results if r.is_correct)

    @property
    def courses_visited(self):
        return len(set(v.course_id for v in self.course_visits))

    @property
    def overall_progress(self):
        """Progreso general 0-100 basado en actividad combinada."""
        quiz_score   = self.avg_quiz_score * 0.4          # 40%
        sim_score    = (self.simulation_correct / max(self.simulation_count, 1)) * 100 * 0.3  # 30%
        course_score = min(self.courses_visited / 4, 1) * 100 * 0.3   # 30% (4 cursos total)
        return round(quiz_score + sim_score + course_score)
