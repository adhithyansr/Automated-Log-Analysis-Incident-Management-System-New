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

        # existing_incident check removed to allow one ticket per log alert
        
        # Prepare content
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

        if action_config.get("priority")==1:
            impact=1
            urgency=1

        elif action_config.get("priority")==2:
            impact=1
            urgency=2

        elif action_config.get("priority")==3:
            impact=2
            urgency=2
        else:
            impact=3
            urgency=3

        payload = {
            "short_description": short_description,
            "description": render_template_string(
                description, context
            ),
            "impact": impact, 
            "urgency": urgency,
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

