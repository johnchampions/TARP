'''
This file should contain the middleware for configuring the reports.
Setting API keys, Breakfast time and such
'''

from sqlalchemy.sql.expression import false
from flasky.tar_helper import get_blacklist
from flask import (
    Blueprint,
    g,
    render_template,
    request,
    flash
)
from flasky.auth import login_required
from flasky.db2 import db_session, init_db
from flasky.models import ConfigKeys, CuisineList, OpeningHours, JobResults, JobList, PostCode, SearchCategories
import json
from re import split

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
                mykey = ConfigKeys(keyname=key, keyvalue=request.form[key])
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

@bp.route('/camelcaselocalities')
def camelcaselocalities():
    myrecords = PostCode.query.all()
    for record in myrecords:
        record.Locality = record.Locality.title()
    db_session.commit()
    flash('Updated Localities format')
    return set_config()

@bp.route('/removeblacklistentries')
def remove_blacklist_entries():
    blacklist = get_blacklist()
    for bannedword in blacklist:
        keyword_records = SearchCategories.query.filter(SearchCategories.category == bannedword).all()
        for keyword_record in keyword_records:
            keyword_record.delete()
    db_session.commit()
    flash('Removed Blacklist Entries')
    return set_config()

@bp.route('/searchtypes', methods=('GET', 'POST',))
def configure_searchtypes():
    if request.method == 'POST':
        categories = ('coffee','license','cuisine','blacklist')
        keywordrecords = CuisineList.query.all()
        for record in keywordrecords:
            for category in categories:
                state = False
                keys = request.form.keys()
                checkbox_name = category + '_' + record.placetype
                if checkbox_name in keys:
                    state = True
                if category == 'coffee':
                    record.coffee = state
                if category == 'license':
                    record.license = state
                if category == 'cuisine':
                    record.cuisine = state
                if category == 'blacklist':
                    record.blacklist = state
        db_session.commit()
        items = get_cuisine_types()
        return render_template('config/keywords.html', items=items)
    else:
        items = get_cuisine_types()
        return render_template('config/keywords.html', items=items)

def get_cuisine_types():
    records = CuisineList.query.all()
    output = []
    for record in records:
        mydict = {'keyword' : record.placetype,
            'coffee' : record.coffee,
            'license' : record.license,
            'cuisine' : record.cuisine,
            'blacklist' : record.blacklist}
        output.append(mydict)
    return output