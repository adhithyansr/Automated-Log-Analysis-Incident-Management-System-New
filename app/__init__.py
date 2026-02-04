from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate
from app.scheduler import start_scheduler

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from .auth.routes import auth_bp
    from .logs.routes import log_bp
    from .alerts.routes import alert_bp
    from app.alerts.history_routes import history_bp

    app.register_blueprint(history_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(alert_bp)

    start_scheduler(app)

    return app