from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from .models import User
from app.models.log_source import LogSource
from app.models.log_entry import LogEntry
from app.models.alert_config import AlertConfig

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    # Find the log source specifically for demo_logs.txt
    demo_source = LogSource.query.filter(LogSource.file_path.contains("demo_logs.txt")).first()
    
    log_count = 0
    demo_source_id = None
    
    if demo_source:
        # Count only logs from this specific source, excluding empty/null messages
        log_count = LogEntry.query.filter_by(source_id=demo_source.id).filter(
            LogEntry.message != None, 
            LogEntry.message != ""
        ).count()
        demo_source_id = demo_source.id
    else:
        log_count = 0

    return render_template(
        "dashboard.html",
        log_count=log_count,
        demo_source_id=demo_source_id,
        alert_count=AlertConfig.query.filter_by(enabled=True).count(),
        source_count=LogSource.query.filter_by(enabled=True).count(),
    )

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# --- User Management (Admin Only) ---

from flask_login import current_user
from flask import abort

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/users")
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template("user_list.html", users=users)

@auth_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
        else:
            new_user = User(username=username, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash(f"User {username} created successfully", "success")
            return redirect(url_for("auth.list_users"))
    
    return render_template("create_user.html")

@auth_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.role = request.form["role"]
        
        new_password = request.form.get("password")
        if new_password and new_password.strip():
            user.set_password(new_password)
            
        db.session.commit()
        flash(f"User {user.username} updated", "success")
        return redirect(url_for("auth.list_users"))

    return render_template("edit_user.html", user=user)

@auth_bp.route("/users/delete/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account", "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} deleted", "success")
    
    return redirect(url_for("auth.list_users"))
