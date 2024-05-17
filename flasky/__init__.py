import os
from flask import Flask
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from turbo_flask import Turbo


from flasky.db import db_session
import flasky.tar
import flasky.configure
import flasky.joblist


db = SQLAlchemy(model_class=Base)

def create_app(test_config=None):
    application = Flask(__name__)
    application.config.from_pyfile('config.py')
    turbo = Turbo(application)
    try:
        os.makedirs(application.instance_path)
    except OSError:
        pass
    db.init_app(application)
    application.register_blueprint(flasky.tar.bp)
    application.register_blueprint(flasky.configure.bp)
    application.register_blueprint(flasky.joblist.bp)

    @application.route('/hello')
    def hello():
        return "<h1 style='color:green'>Hello There!!!</h1>"
    
    @application.route('/')
    def indexpage():
        return render_template('/frontpage/frontpage.html')

    return application

if __name__ == "__main__":
    myapp = create_app()
    myapp.debug = True
    myapp.run()