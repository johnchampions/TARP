from facebook import  get_user_from_cookie, GraphAPI
from flask import Blueprint, g, request, redirect, session
from flask.helpers import url_for
from flask.templating import render_template
import requests
from .models import Users
from .db2 import db_session

FB_APP_ID = "1759360954453645"
FB_APP_NAME = "flasky"
FB_APP_SECRET = "42facf7b53407d259ea295cdbc43598a"

bp = Blueprint('fbsearch', __name__, url_prefix='/fbsearch')

@bp.route('/')
def index():
    if g.user:
        return render_template('/facebook/facebook.html', app_id=FB_APP_ID, app_name=FB_APP_NAME, user=g.user)
    return render_template('/facebook/fblogin.html', app_id=FB_APP_ID, app_name=FB_APP_NAME)

@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@bp.before_request
def get_current_user():
    if session.get('user'):
        g.user = session.get('user')
        return

    result = get_user_from_cookie(cookies=request.cookies, app_id=FB_APP_ID, app_secret=FB_APP_SECRET)
    if result:
        user = Users.query.filter(Users.id == result['uid']).first()

        if not user:
            graph = GraphAPI(result['access_token'])
            profile = graph.get_object('me')
            if 'link' not in profile:
                profile['link'] = ''
            user = Users(id=str(profile['id'], name=profile['name'], profile_url=profile['link'], access_token=result['access_token']))
            db_session.add(user)
        elif user.access_token != result['access_token']:
            user.access_token = result['access_token']

        session['user'] = dict(name=user.name, profile_url=user.profile_url, id=user.id, access_token=user.access_token)
    db_session.commit()
    g.user = session.get('user', None)
