from app import create_app
from app.models.alert_config import AlertConfig
from app.models.log_entry import LogEntry
from app.models.alert_run import AlertRun
from app.logs.analyzer import analyze_logs_for_alert
from app.extensions import db

def test_deduplication():
    app = create_app()
    with app.app_context():
        # Get an alert
        alert = AlertConfig.query.filter_by(id=1).first()
        if not alert:
            print("Alert 1 not found")
            return
            
        print(f"Testing de-duplication for Alert: {alert.name}")
        
        # Reset AlertRun for this alert
        run = AlertRun.query.filter_by(alert_id=alert.id).first()
        if run:
            db.session.delete(run)
            db.session.commit()
            print("Reset AlertRun record.")

        # Step 1: Run for the first time
        # The first run should mark the current max ID as processed (to avoid existing history)
        print("\nStep 1: First Run (Baseline Setup)")
        analyze_logs_for_alert(alert)
        run = AlertRun.query.filter_by(alert_id=alert.id).first()
        print(f"Initial watermark: {run.last_processed_log_id if run else 'None'}")

        # Step 2: Add a new log entry
        print("\nStep 2: Adding a NEW matching log")
        log = LogEntry(message="ERROR DatabaseConnection - TEST LOG 1", timestamp="2026-02-04 02:20:00")
        db.session.add(log)
        db.session.commit()
        new_log_id = log.id
        print(f"Created log ID: {new_log_id}")

        # Step 3: Run analyzer again
        print("\nStep 3: Second Run (Expecting 1 match, 0 duplicates)")
        # Note: process_log_for_alerts is called internally. 
        # I'll just monitor the last_processed_log_id.
        analyze_logs_for_alert(alert)
        run = AlertRun.query.filter_by(alert_id=alert.id).first()
        print(f"Watermark after second run: {run.last_processed_log_id}")
        
        # Step 4: Run analyzer again immediately (no new logs)
        print("\nStep 4: Third Run (Expecting 0 NEW matches)")
        analyze_logs_for_alert(alert)
        run = AlertRun.query.filter_by(alert_id=alert.id).first()
        print(f"Watermark after third run (should be same): {run.last_processed_log_id}")
        
        # Step 5: Verify de-duplication
        # If we didn't have de-duplication, the second run would have processed ALL logs.
        # With it, it only processes logs > initial_id.
        if run.last_processed_log_id == new_log_id:
            print("\n🎉 SUCCESS: De-duplication watermark is working correctly!")
        else:
            print("\n❌ FAILURE: Watermark logic failed.")

if __name__ == "__main__":
    test_deduplication()
