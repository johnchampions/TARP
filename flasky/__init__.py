import os
from flask import Flask
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase



def create_app(test_config=None):
    """Creates Flask App
    input: test configuration
    Output: Flask Application"""
    application = Flask(__name__)
    application.config.from_pyfile('config.py')
    try:
        os.makedirs(application.instance_path)
    except OSError:
        pass
    #db.init_app(application)
    import flasky.tar
    import flasky.configure
    import flasky.joblist
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

""" Runs Flask Application"""
if __name__ == "__main__":
    myapp = create_app()
    myapp.debug = True
    myapp.run()