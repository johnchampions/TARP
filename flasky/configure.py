'''
This file should contain the middleware for configuring the reports.
Setting API keys, Breakfast time and such
'''

from flask import (
    Blueprint,
    g,
    render_template,
    request,
    flash
)
from auth import login_required
from db2 import db_session, init_db
from models import ConfigKeys, OpeningHours, JobResults, JobList, SearchCategories
import json

timefields = ('sundayopen','sundayclose',
    'mondayopen','mondayclose',
    'tuesdayopen','tuesdayclose',
    'wednesdayopen','wednesdayclose',
    'thursdayopen','thursdayclose',
    'fridayopen','fridayclose',
    'saturdayopen','saturdayclose',
)

bp = Blueprint('configure', __name__, url_prefix='/configure')

@bp.route('', methods=('GET', 'POST'))
def set_config():
    if request.method == 'POST':
        for key in request.form.keys():
            if request.form[key] != '':
                mykey = ConfigKeys(keyname=key)
                mykey.keyvalue = request.form[key]
                if ConfigKeys.query.filter(ConfigKeys.keyname == key).first() is None:
                    db_session.add(mykey)
                else:
                    db_session.query(ConfigKeys).filter(ConfigKeys.keyname == key).update({ConfigKeys.keyvalue : request.form[key]}, synchronize_session=False)
                db_session.commit()
    values = {}
    for myrow in ConfigKeys.query.all():
        values[myrow.keyname] = myrow.keyvalue
    flash('Configuration saved.')
    return render_template('config/config.html', values=values)

@bp.route('/cleanopeninghours', methods=('GET',))
def clean_opening_hours():
    OpeningHours.__mapper_args__['confirm_deleted_rows'] = False
    ohrecords = OpeningHours.query.filter().all()
    for record in ohrecords:
        recorddict = record.__dict__
        delthisrecord = True
        for timefield in timefields:
            if recorddict[timefield] is not None:
                delthisrecord = False
                break
        if delthisrecord:
            db_session.delete(record)
    db_session.commit()
    OpeningHours.__mapper_args__['confirm_deleted_rows'] = True
    flash('Opening hours all clean now.')
    return set_config()

@bp.route('/resetdb', methods=('GET',))
def resetdb():
    init_db()
    flash('You now have an initialised database')
    return set_config()
    
@bp.route('/rejiggerjoblist')
def rejigger_job_list():
    joblistrecords = JobList.query.all()
    for joblistrecord in joblistrecords:
        print(joblistrecord.jobjson)
        jobjson = json.loads(joblistrecord.jobjson)
        joblistrecord.address = jobjson['address']
        joblistrecord.radius = jobjson['radius']
        if 'lat' in jobjson:
            joblistrecord.lat = jobjson['lat']
        if 'lng' in jobjson:
            joblistrecord.lng = jobjson['lng'] 
        if 'maxprice' in jobjson:
            joblistrecord.maxprice = jobjson['maxprice']
        if 'minprice' in jobjson:
            joblistrecord.minprice = jobjson['minprice']
        for place in jobjson['placelist']:
            jobresult = JobResults(placeid=place, jobid=joblistrecord.id)
            db_session.add(jobresult)
        if 'types' in jobjson:
            for searchcategory in jobjson['types']:
                searchcategoryrecord = SearchCategories(jobid=joblistrecord.id, category=searchcategory, plugin='googletype')
            db_session.add(searchcategoryrecord)
        if 'categories' in jobjson:
            for searchcategory in jobjson['categories']:
                searchcategoryrecord = SearchCategories(jobid=joblistrecord.id, category=searchcategory, plugin='yelpcategory')
                db_session.add(searchcategoryrecord)
        db_session.merge(joblistrecord)
    db_session.commit()
    flash('Migrated job list to new format')
    return set_config()