SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flask:Merkin12@flaskydb.ckzo2f8bjq9z.ap-southeast-2.rds.amazonaws.com:3306/flasky'
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://connecty:Merkin12@localhost:3306/flasky'
# Uncomment the line below if you want to work with a local DB
SQLALCHEMY_POOL_RECYCLE = 3600

DEBUG = True
WTF_CSRF_ENABLED = True
SECRET_KEY = 'DEV'