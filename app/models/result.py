from app.extensions import db

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    outcome = db.Column(db.String(50))

    __table_args__ = (
        db.Index('ix_result_user_id', 'user_id'),
    )