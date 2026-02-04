from app.alerts.email_executor import execute_email_action
from app.alerts.servicenow_executor import execute_servicenow_action
from app.alerts.throttle import is_throttled
from app.models.alert_execution import AlertExecution
from app.models.log_entry import LogEntry


def process_log_for_alerts(alert, log_data):
    """
    Process a log entry against all actions for an alert.
    Includes strict de-duplication based on log_entry_id.
    """
    # Determine log_id if we have a model object
    log_id = getattr(log_data, 'id', None)

    # Execution Context to share data between actions
    exec_context = {"incident_number": None}

    # 1. Ticket-First execution (ServiceNow)
    sn_action = next((a for a in alert.actions if a.action_type == "servicenow" and a.enabled), None)
    if sn_action:
        # De-duplication check for this log line
        already_executed = False
        if log_id:
            already_executed = AlertExecution.query.filter_by(
                alert_id=alert.id, action_type="servicenow", log_entry_id=log_id, status="SUCCESS"
            ).first()

        if not already_executed:
            throttle_minutes = sn_action.config.get("throttle_minutes")
            if not is_throttled(alert.id, "servicenow", throttle_minutes):
                exec_context["incident_number"] = execute_servicenow_action(alert, sn_action.config, log_data)

    # 2. Notification execution (Email)
    email_action = next((a for a in alert.actions if a.action_type == "email" and a.enabled), None)
    if email_action:
        # De-duplication check for this log line
        already_executed = False
        if log_id:
            already_executed = AlertExecution.query.filter_by(
                alert_id=alert.id, action_type="email", log_entry_id=log_id, status="SUCCESS"
            ).first()

        if not already_executed:
            throttle_minutes = email_action.config.get("throttle_minutes")
            if not is_throttled(alert.id, "email", throttle_minutes):
                execute_email_action(alert, email_action.config, log_data, incident_number=exec_context["incident_number"])

