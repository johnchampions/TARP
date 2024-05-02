import os
from flask import redirect, url_for
from flask.blueprints import Blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook


app_id = '1759360954453645'
bp = make_facebook_blueprint(client_id=app_id)



@bp.route('/')
def index():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    resp = facebook.get('/me')
    assert resp.ok, resp.text
    return 'You are {name} on Facebook'.format(name=resp.json()['name'])
