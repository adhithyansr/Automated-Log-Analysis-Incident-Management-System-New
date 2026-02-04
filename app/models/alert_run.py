from app.extensions import db
from datetime import datetime


class AlertRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    alert_id = db.Column(db.Integer, unique=True, nullable=False)

    last_run_at = db.Column(db.DateTime, nullable=True)
    
    # ID of the last LogEntry processed by this alert to prevent duplicates
    last_processed_log_id = db.Column(db.Integer, nullable=True, default=0)