SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flask:Merkin12@flaskydb.ckzo2f8bjq9z.ap-southeast-2.rds.amazonaws.com:3306/flasky'
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flasky:Merkin12@172.19.80.1:3306/flasky'
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True
SECRET_KEY = 'DEV'

SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = True

    # Flask-Mail SMTP server settings

USER_APP_NAME = "Trade Area Review Program"      # Shown in and email templates and page footers
USER_ENABLE_EMAIL = False        # Enable email authentication
USER_ENABLE_USERNAME = True    # Disable username authentication
USER_EMAIL_SENDER_EMAIL = 'noreply@championsofchange.com.au'
USER_ENABLE_REGISTER = False
