import os
from flask import Flask, config
from flask.templating import render_template
import db2
import auth, tar, configure, scratch, joblist

def indexpage():
    return render_template('frontpage/frontpage.html')

def hello():
    return "<h1 style='color:green'>Hello There!</h1>"

application = Flask(__name__)
application.config.from_pyfile('config.py', silent=True)
application.add_url_rule('/', 'index', indexpage)
application.add_url_rule('/hello', 'hello', hello)
application.register_blueprint(auth.bp)
application.register_blueprint(tar.bp)
application.register_blueprint(configure.bp)
application.register_blueprint(joblist.bp)

@application.teardown_appcontext
def shutdown_session(exception=None):
    db2.db_session.remove()

if __name__ == "__main__":
    application.debug = True
    application.run()
