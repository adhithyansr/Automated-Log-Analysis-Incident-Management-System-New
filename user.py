from app import create_app  
from app.extensions import db
from app.auth.models import User

app = create_app()

in_username = input("Username: ")
in_password = input("Password: ")
in_role = input("Role: ")

with app.app_context():
    user = User(username=in_username.strip(), role=in_role.strip())
    user.set_password(str(in_password).strip())
    db.session.add(user)
    db.session.commit()

print(f"User {in_username} is created.")


