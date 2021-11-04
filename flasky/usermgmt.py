from flask import Blueprint, request
from flask.templating import render_template
from flask_user.decorators import roles_required
from .models import User, Role
from .db import db_session


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
            'admin' : len(my_user_record.roles) > 0}
        userlist.append(userdict)
    return render_template('/usermgmt/usermgmt.html', userlist=userlist)


    
