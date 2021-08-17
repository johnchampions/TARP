import functools
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)
from db2 import db_session
from models import Users

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email_address = request.form['email']
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email_address:
            error = 'Email address is required.'
        elif Users.query.filter(Users.username == username).first() is not None:
            error = 'User {} is already registered.'.format(username)
        
        if error is None:
            u = Users(username, generate_password_hash(password), email_address)
            db_session.add(u)
            db_session.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = Users.query.filter(Users.username == username).first()
        print(user)
        if user is None:
            error = 'Incorrect Username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect Password'
        
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    
    return wrapped_view
