from app.models.alert_config import AlertConfig
from app.alerts.executor import process_log_for_alerts
from app.models.log_entry import LogEntry
from app.models.alert_run import AlertRun
from app.extensions import db


# Note: analyze_log is now obsolete. 
# Log analysis is handled by analyze_logs_for_alert which supports watermarking for de-duplication.


def analyze_logs_for_alert(alert):
    """
    Analyze ONLY NEW log entries for a specific alert since the last run.
    Uses last_processed_log_id to prevent duplication.
    """
    # Get the keyword and trim whitespace
    keyword = alert.keyword.strip() if alert.keyword else ""
    if not keyword:
        return

    # Get the watermark to track processed logs
    run = AlertRun.query.filter_by(alert_id=alert.id).first()
    if not run:
        # Should have been created by scheduler, but fallback just in case
        latest_id = db.session.query(db.func.max(LogEntry.id)).scalar() or 0
        run = AlertRun(alert_id=alert.id, last_processed_log_id=latest_id)
        db.session.add(run)
        db.session.commit()
        return

    last_id = run.last_processed_log_id or 0
    
    # Filter logs: 
    # 1. ONLY logs created AFTER our last seen ID
    # 2. Exclude empty/null messages
    logs = LogEntry.query.filter(
        LogEntry.id > last_id,
        LogEntry.message != None,
        LogEntry.message != ""
    ).order_by(LogEntry.id.asc()).all()
    
    if not logs:
        return



    max_scanned_id = last_id
    for log in logs:
        # Case-insensitive exact phrase matching
        if keyword.lower() in log.message.lower():
            process_log_for_alerts(alert, log)
        
        if log.id > max_scanned_id:
            max_scanned_id = log.id
            
    # Update the watermark so we skip these in the next run
    run.last_processed_log_id = max_scanned_id
    db.session.commit()

