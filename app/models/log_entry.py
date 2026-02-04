from app.extensions import db
from datetime import datetime

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(db.String(50))
    level = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)

    source_id = db.Column(db.Integer, db.ForeignKey("log_source.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.relationship("LogSource", backref="logs")