import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # DB 
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = f"Log Monitor <{os.getenv('MAIL_USERNAME')}>"

    # Service-now
    SERVICENOW_INSTANCE = f"https://{os.getenv('SERVICENOW_INSTANCE')}.service-now.com"
    SERVICENOW_USER = os.getenv('SERVICENOW_USER')
    SERVICENOW_PASSWORD = os.getenv('SERVICENOW_PASSWORD')
