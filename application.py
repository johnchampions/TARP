
from flask import Flask
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flasky.db import db_session
import flasky.tar
import flasky.configure
import flasky.joblist



def indexpage():
    return render_template('/frontpage/frontpage.html')

def hello():
    return "<h1 style='color:green'>Hello There!!!</h1>"



app = Flask(__name__)

app.config.from_pyfile('config.py')

app.add_url_rule('/', 'index', indexpage)
app.add_url_rule('/hello', 'hello', hello)
app.register_blueprint(flasky.tar.bp)
app.register_blueprint(flasky.configure.bp)
app.register_blueprint(flasky.joblist.bp)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.debug = True
    app.run()

