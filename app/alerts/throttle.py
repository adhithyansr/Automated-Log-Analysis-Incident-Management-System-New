from datetime import datetime, timedelta
from app.models.alert_execution import AlertExecution
from app.extensions import db


def is_throttled(alert_id, action_type, throttle_minutes):
    """
    Checks if an alert action is within its throttle window.
    Strictly uses the most recent execution record.
    """
    if not throttle_minutes:
        return False

    # Must check the LATEST record to correctly determine if we are in a quiet period
    record = AlertExecution.query.filter_by(
        alert_id=alert_id,
        action_type=action_type
    ).order_by(AlertExecution.triggered_at.desc()).first()

    if not record:
        return False

    next_allowed_time = record.triggered_at + timedelta(minutes=throttle_minutes)
    return datetime.now() < next_allowed_time


def record_execution(alert_id, action_type):
    """
    Records a new execution pulse (used for throttling).
    Note: Most executors add their own detail-rich AlertExecution records.
    """
    now = datetime.now()

    # We update the latest record or create a new one to mark the 'pulse'
    record = AlertExecution.query.filter_by(
        alert_id=alert_id,
        action_type=action_type
    ).order_by(AlertExecution.triggered_at.desc()).first()

    if record:
        record.triggered_at = now
    else:
        db.session.add(AlertExecution(
            alert_id=alert_id,
            action_type=action_type,
            status="SUCCESS",
            triggered_at=now
        ))

    db.session.commit()
