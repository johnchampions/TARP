ENVIRONMENT = 'PROD'

if ENVIRONMENT == 'DEV':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/tarp.sqlite3'
    URL = 'http://127.0.0.1/'
    SECRET_KEY = 'DEV'
if ENVIRONMENT == 'PROD':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/tarp.sqlite3'
    URL = 'https://futurefoodtarp.azurewebsites.net/'
    SECRET_KEY = 'dbe7f9ab0ed7c797356d9988dd86b22d6a63bc6b65fad8d3bcb0f4c0940ef0a3'


SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = True
WTF_CSRF_ENABLED = True
