from app.extensions import db
import json

class AlertAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alert_config.id"))
    action_type = db.Column(db.String(50))
    config = db.Column(db.JSON)
    enabled = db.Column(db.Boolean, default=True)