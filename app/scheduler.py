from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from app.extensions import db
from app.models.alert_run import AlertRun
from app.models.alert_config import AlertConfig
from app.models.log_source import LogSource
from app.models.log_entry import LogEntry

from app.logs.ingestor import ingest_logs_from_source
from app.logs.analyzer import analyze_logs_for_alert


def run_scheduled_alerts():
    """
    Main scheduler logic.
    Runs every minute.
    """
    now = datetime.now()

    # --------------------------------------------------
    # Ingest logs from all enabled sources
    # --------------------------------------------------
    sources = LogSource.query.filter_by(enabled=True).all()

    for source in sources:
        try:
            ingest_logs_from_source(source)
        except Exception as e:
            # In production, log this properly
            print(f"[Scheduler] Failed to ingest source {source.file_path}: {e}")

    # --------------------------------------------------
    # Execute alerts based on interval
    # --------------------------------------------------
    alerts = AlertConfig.query.filter_by(enabled=True).all()

    for alert in alerts:
        run = AlertRun.query.filter_by(alert_id=alert.id).first()

        # 1. Initialize for NEW alerts if they don't have a run record yet
        if not run:
            # Important: Get max ID to initialize watermark so we don't alert on past logs
            latest_id = db.session.query(db.func.max(LogEntry.id)).scalar() or 0
            run = AlertRun(
                alert_id=alert.id,
                last_run_at=now,
                last_processed_log_id=latest_id
            )
            db.session.add(run)
            db.session.commit()
            print(f"[Scheduler] Initialized watermark for alert {alert.id} at {latest_id}")
            should_run = True
        else:
            # 2. Check run interval
            if not run.last_run_at:
                should_run = True
            else:
                next_run_time = run.last_run_at + timedelta(minutes=alert.interval_minutes)
                should_run = now >= next_run_time

        if not should_run:
            continue

        try:
            # 🕒 Update last run time IMMEDIATELY to prevent overlaps if analysis is slow
            run.last_run_at = now
            db.session.add(run)
            db.session.commit()

            # 🔍 Run alert search (now uses watermark to check ONLY logs created since last_processed_log_id)
            analyze_logs_for_alert(alert)

        except Exception as e:
            db.session.rollback()
            print(f"[Scheduler] Alert {alert.id} failed: {e}")


def scheduler_job(app):
    """
    Wrapper to ensure Flask app context.
    """
    with app.app_context():
        run_scheduled_alerts()


def start_scheduler(app):
    """
    Starts APScheduler.
    Called once during app startup.
    """
    scheduler = BackgroundScheduler(daemon=True)

    scheduler.add_job(
        func=lambda: scheduler_job(app),
        trigger="interval",
        minutes=1,
        id="alert_scheduler",
        replace_existing=True,
    )

    scheduler.start()
