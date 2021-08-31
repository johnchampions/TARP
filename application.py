import os
from flask import Flask, config
from flask.templating import render_template
import flasky.db2 as db2
import flasky.auth, flasky.tar, flasky.configure, flasky.joblist

def indexpage():
    return render_template('frontpage/frontpage.html')

def hello():
    return "<h1 style='color:green'>Hello There!</h1>"

application = Flask(__name__)
application.config.from_pyfile('config.py', silent=True)
application.add_url_rule('/', 'index', indexpage)
application.add_url_rule('/hello', 'hello', hello)
application.register_blueprint(flasky.auth.bp)
application.register_blueprint(flasky.tar.bp)
application.register_blueprint(flasky.configure.bp)
application.register_blueprint(flasky.joblist.bp)

@application.teardown_appcontext
def shutdown_session(exception=None):
    db2.db_session.remove()

if __name__ == "__main__":
    application.debug = True
    application.run()
