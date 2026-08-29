from datetime import datetime
from app.extensions import db


class QuizResult(db.Model):
    __tablename__ = 'quiz_result'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score      = db.Column(db.Integer, nullable=False)
    correct    = db.Column(db.Integer, nullable=False)
    total      = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('ix_quizresult_user_created', 'user_id', 'created_at'),
        db.Index('ix_quizresult_score', 'score'),
    )

    def __repr__(self):
        return f'<QuizResult user={self.user_id} score={self.score}>'


class SimulationResult(db.Model):
    __tablename__ = 'simulation_result'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario_id  = db.Column(db.String(20), nullable=False)
    action_taken = db.Column(db.String(30), nullable=False)
    is_correct   = db.Column(db.Boolean, nullable=False)
    points       = db.Column(db.Integer, default=0)
    risk_level   = db.Column(db.String(10), default='medio')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('ix_simresult_user_created', 'user_id', 'created_at'),
        db.Index('ix_simresult_scenario_correct', 'scenario_id', 'is_correct'),
        db.Index('ix_simresult_user_scenario', 'user_id', 'scenario_id'),
    )

    def __repr__(self):
        return f'<SimulationResult user={self.user_id} scenario={self.scenario_id}>'


class CourseVisit(db.Model):
    __tablename__ = 'course_visit'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id  = db.Column(db.String(30), nullable=False)
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('ix_coursevisit_user_course', 'user_id', 'course_id'),
        db.Index('ix_coursevisit_visited_at', 'visited_at'),
    )

    def __repr__(self):
        return f'<CourseVisit user={self.user_id} course={self.course_id}>'


class SimulationProgress(db.Model):
    """Progreso de simulaciones inmersivas (multi-etapa)."""
    __tablename__ = 'simulation_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario_id = db.Column(db.String(20), nullable=False)
    current_stage = db.Column(db.String(30), nullable=True)
    completed_stages = db.Column(db.JSON, default=list)
    total_points = db.Column(db.Integer, default=0)
    choices = db.Column(db.JSON, default=dict)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.Index('ix_simprogress_user_scenario', 'user_id', 'scenario_id'),
        db.Index('ix_simprogress_updated_at', 'updated_at'),
    )

    def __repr__(self):
        return f'<SimulationProgress user={self.user_id} scenario={self.scenario_id} stage={self.current_stage}>'

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    @property
    def progress_percentage(self) -> float:
        """Porcentaje de etapas completadas (estimado)."""
        # Se calcula dinámicamente según el escenario
        return 0.0
