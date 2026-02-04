from app.utils.servicenow_client import create_incident, check_existing_incident
from app.utils.template_renderer import render_template_string
from app.models.alert_execution import AlertExecution
from app.extensions import db
from datetime import datetime


def execute_servicenow_action(alert, action_config, log_data):
    try:
        context = {
            "alert_name": alert.name,
            "keyword": alert.keyword,
            "log_message": log_data.message,
            "timestamp": log_data.timestamp,
        }

        short_description = render_template_string(
            action_config["short_description"], context
        )

        existing_incident = check_existing_incident(short_description)

        if existing_incident:
             db.session.add(AlertExecution(
                alert_id=alert.id,
                log_entry_id=getattr(log_data, 'id', None),
                action_type="servicenow",
                status="SUCCESS",
                message=f"Skipped creation: Duplicate incident {existing_incident['number']} exists"
            ))
             db.session.commit()
             return existing_incident['number']
        else:
            # ... (log details logic kept same) ...
            # (assuming the replacement chunk will handle the content accurately)
            # Rebuilding the block to ensure correct context
            include_log = action_config.get("include_log", False)
            if include_log:
                log_details = f"""
--------------------------------------------------
MATCHED LOG DETAILS
--------------------------------------------------
Timestamp: {log_data.timestamp}
Message: {log_data.message}
--------------------------------------------------
"""
                description = action_config["description"] + "\n" + log_details
            else:
                description = action_config["description"]

            payload = {
                "short_description": short_description,
                "description": render_template_string(
                    description, context
                ),
                "priority": action_config.get("priority", "3"),
            }

            result = create_incident(payload)
            incident_number = result["result"].get("number", "UNKNOWN")

            db.session.add(AlertExecution(
                alert_id=alert.id,
                log_entry_id=getattr(log_data, 'id', None),
                action_type="servicenow",
                status="SUCCESS",
                message=f"Incident {incident_number} created",
                triggered_at=datetime.now()
            ))
            db.session.commit()
            return incident_number

    except Exception as e:
        db.session.add(AlertExecution(
            alert_id=alert.id,
            action_type="servicenow",
            status="FAILED",
            message=str(e)
        ))
        db.session.commit()
    return None

