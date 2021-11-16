from flask import Blueprint, request, url_for, current_app
from flask.helpers import flash
from flask.templating import render_template
from flask_user.decorators import roles_required
from werkzeug.utils import redirect
from .models import User, Role
from .db import db_session
from flask_user import PasswordManager


bp = Blueprint('usermgmt', __name__, url_prefix='/usermgmt')

@bp.route('/', methods=('GET', 'POST'))
@roles_required('admin')
def displaydialog():
    my_user_records = User.query.all()
    if request.method == 'POST':
        my_role_record = Role.query.filter(Role.name == 'admin').first()
        for my_user_record in my_user_records:
            if my_user_record.username + '.delete' in request.form:
                db_session.delete(my_user_record)
            if my_user_record.username + '.role' in request.form:
                if my_role_record not in my_user_record.roles:
                    my_user_record.roles.append(my_role_record)
            else:    
                if my_role_record in my_user_record.roles:
                    my_user_record.roles.remove(my_role_record)
        db_session.commit()
    userlist = []
    for my_user_record in User.query.all():
        userdict ={'username' : my_user_record.username,
            'admin' : len(my_user_record.roles) > 0,
            'id' : my_user_record.id }
        userlist.append(userdict)
    return render_template('/usermgmt/usermgmt.html', userlist=userlist)

@bp.route('/edituser/<int:user_id>', methods=('GET','POST',))
@roles_required('admin')
def edit_user(user_id):
    error = None
    my_user_record = User.query.filter(User.id == user_id).first()
    if my_user_record is None:
        error = 'User could not be found'
    if request.method == 'GET':
        output = dict( name = my_user_record.username,
            id = user_id,
            first_name = my_user_record.first_name,
            last_name = my_user_record.last_name,
            admin = len(my_user_record.roles) > 0)
        if error is None:
            return render_template('/usermgmt/edituser.html', record=output)
        else:
            flash(error)
            return redirect('/usermgmt/')
    if request.method == 'POST':
        my_password_manager = PasswordManager(current_app)
        my_role_record = Role.query.filter(Role.name == 'admin').first()
        if request.form['password'] == '' :
            error = 'Password cannot be blank'
        if request.form['password'] != request.form['retype_password']:
            error = 'Passwords don\'t match.'
        if request.form['username'] == '':
            error = 'Username cannot be blank'
        if error is None:
            my_user_record.username = request.form['username']
            my_user_record.password = my_password_manager.hash_password(request.form['password'],)
            my_user_record.first_name = request.form['first_name']
            my_user_record.last_name = request.form['last_name']
            if 'admin' in request.form:
                if my_role_record not in my_user_record.roles:
                    my_user_record.roles.append(my_role_record)
            else:    
                if my_role_record in my_user_record.roles:
                    my_user_record.roles.remove(my_role_record)
            db_session.commit()
        if error is not None:
            flash(error)
            return redirect('/usermgmt/edituser/' + str(user_id))
        return redirect('/usermgmt/')

@bp.route('/newuser', methods=('GET','POST',))
@roles_required('admin')
def new_user():
    error = None
    if request.method == 'GET':
        output = dict( name = '',
            first_name = '',
            last_name = '',
            admin = 0)
        return render_template('/usermgmt/edituser.html', record=output)
    if request.method == 'POST':
        my_password_manager = PasswordManager(current_app)
        my_role_record = Role.query.filter(Role.name == 'admin').first()
        if request.form['password'] == '' :
            error = 'Password cannot be blank'
        if request.form['password'] != request.form['retype_password']:
            error = 'Passwords don\'t match.'
        if request.form['username'] == '':
            error = 'Username cannot be blank'
        if error is None:
            my_user_record = User(username=request.form['username'],
                password=my_password_manager.hash_password(request.form['password']),
                first_name=request.form['first_name'],
                last_name=request.form['last_name'])
            db_session.add(my_user_record)
            db_session.commit()
            if 'admin' in request.form:
                my_user_record.roles.append(my_role_record)
                db_session.commit()
        return redirect('/usermgmt/')




        

        
        
    

        



    
