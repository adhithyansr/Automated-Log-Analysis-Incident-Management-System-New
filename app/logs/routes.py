from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from flask_login import login_required
from app.utils.decorators import admin_required
from .parser import parse_log_file
from app.models.log_source import LogSource
from app.extensions import db
from app.models.log_entry import LogEntry


log_bp = Blueprint("logs", __name__, url_prefix="/logs")

# Admin only
@log_bp.route("/add-source", methods=["GET", "POST"])
@login_required
@admin_required
def add_log_source():
    if request.method == "POST":
        name = request.form["name"]
        file_path = request.form["file_path"]

        source = LogSource(
            name=name,
            file_path=file_path
        )
        db.session.add(source)
        db.session.commit()

        flash("Log source added successfully", "success")
        return redirect(url_for("logs.add_log_source"))

    return render_template("add_log_source.html")


@log_bp.route("/sources")
@login_required
def list_log_sources():
    sources = LogSource.query.order_by(LogSource.id.desc()).all()
    return render_template("log_sources.html", sources=sources)


@log_bp.route("/sources/toggle/<int:source_id>")
@login_required
@admin_required
def toggle_log_source(source_id):
    source = LogSource.query.get_or_404(source_id)
    source.enabled = not source.enabled
    db.session.commit()
    return redirect(url_for("logs.list_log_sources"))

@log_bp.route("/sources/edit/<int:source_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_log_source(source_id):
    source = LogSource.query.get_or_404(source_id)

    if request.method == "POST":
        new_name = request.form["name"]
        new_path = request.form["file_path"]
        enabled = "enabled" in request.form
        reset_offset = "reset_offset" in request.form

        # Detect path change
        path_changed = new_path != source.file_path

        source.name = new_name
        source.file_path = new_path
        source.enabled = enabled

        # Reset offset if requested OR path changed
        if reset_offset or path_changed:
            source.last_read_offset = 0

        db.session.commit()

        flash("Log source updated successfully", "success")
        return redirect(url_for("logs.list_log_sources"))

    return render_template("edit_log_source.html", source=source)


# Admin + User
@log_bp.route("/search", methods=["GET", "POST"])
@login_required
def search_logs():
    results = []
    keyword = ""
    start_time = ""
    end_time = ""
    source_id = request.args.get("source_id", type=int)
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%dT%H:%M")

    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        start_time = request.form.get("start_time", "")
        end_time = request.form.get("end_time", "")
        source_id = request.form.get("source_id", type=int)

    if keyword or start_time or end_time or source_id:
        # Base query: exclude empty or null messages
        query = LogEntry.query.filter(LogEntry.message != None, LogEntry.message != "")

        if keyword:
            query = query.filter(LogEntry.message.ilike(f"%{keyword}%"))
            
        if source_id:
            query = query.filter(LogEntry.source_id == source_id)

        if start_time:
            try:
                s_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
                if s_dt > now_dt:
                    flash("Start Time cannot be in the future.", "warning")
                else:
                    query = query.filter(LogEntry.created_at >= s_dt)
            except ValueError:
                flash("Invalid Start Time format", "warning")

        if end_time:
            try:
                e_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
                if e_dt > now_dt:
                    flash("End Time cannot be in the future. Clamping to current time.", "info")
                    e_dt = now_dt
                
                if start_time:
                    s_dt_check = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
                    if s_dt_check >= e_dt:
                        flash("Start Time must be before End Time.", "warning")
                        return redirect(url_for("logs.search_logs"))
                
                query = query.filter(LogEntry.created_at <= e_dt)
            except ValueError:
                flash("Invalid End Time format", "warning")

        results = query.order_by(LogEntry.created_at.desc()).all()
    elif request.method == "POST":
        flash("Please enter a keyword or select a time range.", "warning")
        return redirect(url_for("logs.search_logs"))

    return render_template(
        "search_logs.html", 
        results=results, 
        keyword=keyword,
        start_time=start_time,
        end_time=end_time,
        source_id=source_id,
        now=now_str
    )
