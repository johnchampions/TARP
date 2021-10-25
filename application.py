import os
from flask import Flask, app, config
from flask.templating import render_template
from flasky.db import db_session
import flasky.auth
import flasky.tar
import flasky.configure
import flasky.joblist
import flasky.facebook


def indexpage():
    return render_template('frontpage/frontpage.html')

def hello():
    return "<h1 style='color:green'>Hello There!</h1>"


application = Flask(__name__)
application.config.from_pyfile('config.py')
application.add_url_rule('/', 'index', indexpage)
application.add_url_rule('/hello', 'hello', hello)
application.register_blueprint(flasky.auth.bp)
application.register_blueprint(flasky.tar.bp)
application.register_blueprint(flasky.configure.bp)
application.register_blueprint(flasky.joblist.bp)
application.register_blueprint(flasky.facebook.bp)

@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    application.debug = True
    application.port = 443
    application.ssl_context = 'adhoc'
    application.run()

