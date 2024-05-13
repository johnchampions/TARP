ENVIRONMENT = 'DEVPOST'

if ENVIRONMENT == 'DEV':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/tarp.sqlite3'
    URL = 'http://127.0.0.1/'
    SECRET_KEY = 'DEV'
if ENVIRONMENT == 'PROD':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/tarp.sqlite3'
    URL = 'http://tarp.local/'
    SECRET_KEY = 'dbe7f9ab0ed7c797356d9988dd86b22d6a63bc6b65fad8d3bcb0f4c0940ef0a3'
if ENVIRONMENT == 'DEVPOST':
    SQLALCHEMY_DATABASE_URI = 'postgresql+pg8000://postgres:Merkin12@192.168.123.249/flasky'
    URL = 'http://tarp.local/'
    SECRET_KEY = 'dbe7f9ab0ed7c797356d9988dd86b22d6a63bc6b65fad8d3bcb0f4c0940ef0a3'



SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = True
WTF_CSRF_ENABLED = True
    # Flask-Mail SMTP server settings

USER_APP_NAME = "Trade Area Review Program"      # Shown in and email templates and page footers
USER_ENABLE_EMAIL = False        # Enable email authentication
USER_ENABLE_USERNAME = True    # Disable username authentication
USER_EMAIL_SENDER_EMAIL = 'noreply@championsofchange.com.au'
USER_ENABLE_REGISTER = False


