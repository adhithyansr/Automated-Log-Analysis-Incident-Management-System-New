from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.alert_execution import AlertExecution
from app.models.alert_config import AlertConfig

history_bp = Blueprint("history", __name__, url_prefix="/alerts/history")

@history_bp.route("/")
@login_required
def alert_history():
    """
    Redirect to the consolidated alerts page's history section.
    """
    return redirect(url_for('alerts.list_alerts') + '#history')
