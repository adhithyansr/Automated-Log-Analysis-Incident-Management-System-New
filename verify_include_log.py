from app import create_app
from app.models.alert_config import AlertConfig
from app.models.log_entry import LogEntry
from app.models.alert_action import AlertAction
from app.alerts.executor import process_log_for_alerts
from app.extensions import db
import json

def test_include_log_formatting():
    app = create_app()
    with app.app_context():
        # Get an alert
        alert = AlertConfig.query.filter_by(id=1).first()
        if not alert:
            print("Alert 1 not found")
            return
            
        print(f"Testing Include Log formatting for Alert: {alert.name}")
        
        # Ensure email action has include_log=True
        email_action = AlertAction.query.filter_by(alert_id=alert.id, action_type='email').first()
        if not email_action:
            print("Email action not found")
            return
            
        config = email_action.config
        config['include_log'] = True
        config['to'] = ['test@example.com']
        email_action.config = config
        db.session.add(email_action)
        db.session.commit()
        print("Set include_log=True in config.")

        # Create a log entry
        log_data = LogEntry(
            message="ERROR DatabaseConnection - TEST LOG FOR FORMATTING", 
            timestamp="2026-02-04 02:30:00"
        )
        
        # We need to mock send_email or just check the AlertExecution message
        # In email_executor.py, I added:
        # db.session.add(AlertExecution(..., message=f"Email sent successfully to {', '.join(action_config['to'])}"))
        
        print("\nTriggering alert...")
        process_log_for_alerts(alert, log_data)
        db.session.commit()
        
        # Check AlertExecution
        from app.models.alert_execution import AlertExecution
        execution = AlertExecution.query.order_by(AlertExecution.id.desc()).first()
        print(f"\nExecution Status: {execution.status}")
        print(f"Execution Message (Trace): {execution.message}")
        
        if execution.status == "SUCCESS":
            print("\n🎉 SUCCESS: Alert triggered correctly with include_log=True.")
        else:
            print(f"\n❌ FAILURE: Alert execution failed. Error: {execution.message}")

if __name__ == "__main__":
    test_include_log_formatting()
