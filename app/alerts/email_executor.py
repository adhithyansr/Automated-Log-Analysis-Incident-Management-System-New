from app.utils.email_service import send_email
from app.utils.template_renderer import render_template_string
from app.models.alert_execution import AlertExecution
from app.extensions import db
from datetime import datetime

def execute_email_action(alert, action_config, log_data, incident_number=None):
    try:
        context = {
            "alert_name": alert.name,
            "keyword": alert.keyword,
            "log_message": log_data.message,
            "timestamp": log_data.timestamp,
            "incident_number": incident_number,
        }

        subject = render_template_string(
            action_config["subject"], context
        )

        # Handle user's choice to include log details
        include_log = action_config.get("include_log", False)
        
        # Prepare the base body with incident info if available
        base_body = action_config["body"]
        if incident_number:
            ticket_info = f"\n\n🎫 ServiceNow Incident Created: {incident_number}\n"
            base_body += ticket_info

        if include_log:
            # Format the log details section
            log_details = f"""
--------------------------------------------------
MATCHED LOG DETAILS
--------------------------------------------------
Timestamp: {log_data.timestamp}
Log Message: {log_data.message}
--------------------------------------------------
"""
            email_body = base_body + "\n" + log_details
        else:
            email_body = base_body
            
        body = render_template_string(
            email_body, context
        )

        send_email(
            to_addresses=action_config["to"],
            subject=subject,
            body=body,
            importance=action_config.get("importance", "normal")
        )


        success_msg = f"Email sent successfully to {', '.join(action_config['to'])}"
        if incident_number:
            success_msg += f" (Linked Incident: {incident_number})"

        db.session.add(AlertExecution(
            alert_id=alert.id,
            log_entry_id=getattr(log_data, 'id', None),
            action_type="email",
            status="SUCCESS",
            message=success_msg,
            triggered_at=datetime.now()
        ))

        db.session.commit()

    except Exception as e:
        db.session.add(AlertExecution(
            alert_id=alert.id,
            action_type="email",
            status="FAILED",
            message=str(e)
        ))
        db.session.commit()