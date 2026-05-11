from datetime import datetime
from app import db


class QuizResult(db.Model):
    __tablename__ = 'quiz_result'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score      = db.Column(db.Integer, nullable=False)          # 0-100
    correct    = db.Column(db.Integer, nullable=False)          # respuestas correctas
    total      = db.Column(db.Integer, nullable=False)          # total preguntas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<QuizResult user={self.user_id} score={self.score}>'


class SimulationResult(db.Model):
    __tablename__ = 'simulation_result'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario_id  = db.Column(db.String(20), nullable=False)     # ej: "sc_001"
    action_taken = db.Column(db.String(30), nullable=False)     # ej: "report"
    is_correct   = db.Column(db.Boolean, nullable=False)
    points       = db.Column(db.Integer, default=0)
    risk_level   = db.Column(db.String(10), default='medio')    # alto/medio/bajo
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SimulationResult user={self.user_id} scenario={self.scenario_id}>'


class CourseVisit(db.Model):
    __tablename__ = 'course_visit'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id  = db.Column(db.String(30), nullable=False)       # ej: "redes", "phishing"
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CourseVisit user={self.user_id} course={self.course_id}>'
