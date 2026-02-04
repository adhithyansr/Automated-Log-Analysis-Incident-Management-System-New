import smtplib
from email.message import EmailMessage
from flask import current_app


def send_email(to_addresses, subject, body, importance="normal"):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    msg["To"] = ", ".join(to_addresses)

    if importance == "high":
        msg["X-Priority"] = "1"
        msg["Importance"] = "High"

    msg.set_content(body)

    with smtplib.SMTP(
        current_app.config["MAIL_SERVER"],
        current_app.config["MAIL_PORT"]
    ) as server:
        if current_app.config["MAIL_USE_TLS"]:
            server.starttls()

        server.login(
            current_app.config["MAIL_USERNAME"],
            current_app.config["MAIL_PASSWORD"]
        )
        server.send_message(msg)