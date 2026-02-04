from app.extensions import db
from datetime import datetime


class AlertExecution(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    alert_id = db.Column(
        db.Integer,
        db.ForeignKey("alert_config.id"),
        nullable=False
    )

    log_entry_id = db.Column(
        db.Integer,
        db.ForeignKey("log_entry.id"),
        nullable=True
    )

    action_type = db.Column(db.String(50), nullable=False)

    status = db.Column(db.String(20), nullable=False)

    message = db.Column(db.Text)

    triggered_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    alert = db.relationship("AlertConfig", backref=db.backref("executions", lazy=True))
    log_entry = db.relationship("LogEntry", backref=db.backref("executions", lazy=True))

    
