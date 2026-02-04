from app.extensions import db

class LogSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)

    enabled = db.Column(db.Boolean, default=True)

    # For incremental reading (later use)
    last_read_offset = db.Column(db.Integer, default=0)