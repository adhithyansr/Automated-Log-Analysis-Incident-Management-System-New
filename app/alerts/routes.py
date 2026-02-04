from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.alert_config import AlertConfig
import json
from app.models.alert_action import AlertAction 
from app.models.log_entry import LogEntry
from app.models.alert_execution import AlertExecution
from app.models.alert_run import AlertRun

alert_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@alert_bp.route("/")
@login_required
def list_alerts():
    """
    All users can view all alerts and history.
    """
    alerts = AlertConfig.query.order_by(AlertConfig.id.desc()).all()
    history = AlertExecution.query.order_by(AlertExecution.triggered_at.desc()).all()

    return render_template("alert_list.html", alerts=alerts, history=history)


@alert_bp.route("/toggle/<int:alert_id>")
@login_required
def toggle_alert(alert_id):
    alert = AlertConfig.query.get_or_404(alert_id)

    # Users can toggle only their own alerts
    if current_user.role != "admin" and alert.user_id != current_user.id:
        return "Unauthorized", 403

    alert.enabled = not alert.enabled
    db.session.commit()

    return redirect(url_for("alerts.list_alerts"))

@alert_bp.route("/edit/<int:alert_id>", methods=["GET", "POST"])
@login_required
def edit_alert(alert_id):
    alert = AlertConfig.query.get_or_404(alert_id)

    # Security: user can edit only own alerts (admin can edit all)
    if current_user.role != "admin" and alert.user_id != current_user.id:
        return "Unauthorized", 403

    email_action = AlertAction.query.filter_by(
        alert_id=alert.id, action_type="email"
    ).first()

    sn_action = AlertAction.query.filter_by(
        alert_id=alert.id, action_type="servicenow"
    ).first()

    if request.method == "POST":
        alert.name = request.form["name"]
        alert.keyword = request.form["keyword"]
        alert.interval_minutes = int(request.form["interval_minutes"])
        alert.enabled = "enabled" in request.form

        if "email_action" in request.form:
            email_config = {
                "to": request.form.get("email_to", "").split(","),
                "subject": request.form.get("email_subject"),
                "body": request.form.get("email_body"),
                "importance": request.form.get("email_importance", "normal"),
                "throttle_minutes": int(request.form.get("email_throttle") or 5),
                "include_log": "email_include_log" in request.form,
            }

            if email_action:
                email_action.config = email_config
            else:
                db.session.add(AlertAction(
                    alert_id=alert.id,
                    action_type="email",
                    config=email_config
                ))
        else:
            if email_action:
                db.session.delete(email_action)

        # ---- SERVICENOW ACTION ----
        if "sn_action" in request.form:
            sn_config = {
                "priority": request.form.get("sn_priority"),
                "short_description": request.form.get("sn_short_desc"),
                "description": request.form.get("sn_description"),
                "throttle_minutes": int(request.form.get("sn_throttle") or 5),
                "include_log": "sn_include_log" in request.form,
            }

            if sn_action:
                sn_action.config = sn_config
            else:
                db.session.add(AlertAction(
                    alert_id=alert.id,
                    action_type="servicenow",
                    config=sn_config
                ))
        else:
            if sn_action:
                db.session.delete(sn_action)



        db.session.commit()
        flash("Alert updated successfully", "success")
        return redirect(url_for("alerts.list_alerts"))

    return render_template("edit_alert.html", alert=alert,email_action=email_action, sn_action=sn_action)

@alert_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_alert():
    if request.method == "POST":
        keyword = request.form["keyword"].strip()

        # Get multiple actions
        email_selected = "email_action" in request.form
        sn_selected = "sn_action" in request.form

        if not email_selected and not sn_selected:
            return "At least one action must be selected", 400

        alert = AlertConfig(
            name=request.form["name"],
            keyword=request.form["keyword"],
            user_id=current_user.id,
            interval_minutes=int(request.form["interval_minutes"]),
        )
        db.session.add(alert)
        db.session.flush()  # get alert.id

        # Email action
        if "email_action" in request.form:
            email_config = {
                "to": request.form["email_to"].split(","),
                "subject": request.form["email_subject"],
                "body": request.form["email_body"],
                "importance": request.form["email_importance"],
                "throttle_minutes": 1 ,#int(request.form["email_throttle"] or 0),
                "include_log": "email_include_log" in request.form,
            }

            db.session.add(AlertAction(
                alert_id=alert.id,
                action_type="email",
                config=email_config
            ))

        # ServiceNow action
        if "sn_action" in request.form:
            sn_config = {
                "priority": request.form["sn_priority"],
                "short_description": request.form["sn_short_desc"],
                "description": request.form["sn_description"],
                "throttle_minutes": 1, #int(request.form["sn_throttle"] or 0),
                "include_log": "sn_include_log" in request.form,
            }

            db.session.add(AlertAction(
                alert_id=alert.id,
                action_type="servicenow",
                config=sn_config
            ))

        # 🚀 IMMEDIATE Watermark to ensure 'No History' for new alerts
        latest_id = db.session.query(db.func.max(LogEntry.id)).scalar() or 0
        db.session.add(AlertRun(
            alert_id=alert.id,
            last_run_at=None, # Scheduler will set this on first run
            last_processed_log_id=latest_id
        ))

        db.session.commit()

        return redirect(url_for("alerts.list_alerts"))

    return render_template("create_alert.html")
