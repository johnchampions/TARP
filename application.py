
from flask import Flask
from flask.templating import render_template
from flask_user import UserManager
from flask_sqlalchemy import SQLAlchemy
from turbo_flask import Turbo
from flasky.db import db_session
from flasky.models import User
import flasky.tar
import flasky.configure
import flasky.joblist
#import flasky.facebook
import flasky.usermgmt


def indexpage():
    return render_template('/frontpage/frontpage.html')

def hello():
    return "<h1 style='color:green'>Hello There!!!</h1>"



application = Flask(__name__)
#turbo = Turbo()
application.config.from_pyfile('config.py')
user_manager = UserManager(application, SQLAlchemy(application), UserClass=User)
#turbo.init_app(application)
application.add_url_rule('/', 'index', indexpage)
application.add_url_rule('/hello', 'hello', hello)
application.register_blueprint(flasky.tar.bp)
application.register_blueprint(flasky.configure.bp)
application.register_blueprint(flasky.joblist.bp)
#application.register_blueprint(flasky.facebook.bp)
application.register_blueprint(flasky.usermgmt.bp)


@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    application.debug = True
    #application.port = 443
    #application.ssl_context = 'adhoc'
    application.run()

