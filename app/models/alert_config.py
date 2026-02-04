from app.extensions import db

class AlertConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    keyword = db.Column(db.String(255), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    interval_minutes = db.Column(db.Integer, nullable=False, default=5)
    
    actions = db.relationship(
        "AlertAction",
        backref="alert",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    user = db.relationship("User", backref="alerts", lazy=True)
