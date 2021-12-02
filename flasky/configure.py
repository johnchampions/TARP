'''
This file should contain the middleware for configuring the reports.
Setting API keys, Breakfast time and such
'''

from flask_user.decorators import roles_required
from .tar_helper import get_blacklist
from flask import (
    Blueprint,
    g,
    render_template,
    request,
    flash
)
from .auth import login_required
from .db import db_session, init_db
from .models import ConfigKeys, CuisineList, GooglePlace, OpeningHours, JobResults, JobList, Places, PostCode, SearchCategories, YelpPlace, ZomatoPlace
import json
from .gs import googleplace
from .ys import yelpplace
from .zs import zomatoplace


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
@roles_required('admin')
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
@roles_required('admin')
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
@roles_required('admin')
def resetdb():
    init_db()
    flash('You now have an initialised database')
    return set_config()
    
@bp.route('/rejiggerjoblist')
@roles_required('admin')
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
@roles_required('admin')
def camelcaselocalities():
    myrecords = PostCode.query.all()
    for record in myrecords:
        record.Locality = record.Locality.title()
    db_session.commit()
    flash('Updated Localities format')
    return set_config()

@bp.route('/removeblacklistentries')
@roles_required('admin')
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
@roles_required('admin')
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

@bp.route('/updateplaces')
@roles_required('admin')
def refresh_places():
    myplacerecords = Places.query.all()
    for myplacerecord in myplacerecords:
        if myplacerecord.googleplaceid is not None:
            my_google_place_record = GooglePlace.query.filter(GooglePlace.id == myplacerecord.googleplaceid).first()
            try:
                my_googleplace = googleplace(my_google_place_record.googleplace_id, refresh=True)
                my_googleplace.set_googleplaceid()
                my_googleplace.set_placeid(myplacerecord.id)
                my_googleplace.set_categories()
                my_googleplace.openinghours_to_db()
            except:
                pass
        if myplacerecord.yelpplaceid is not None:
            my_yelp_place_record = YelpPlace.query.filter(YelpPlace.id == myplacerecord.yelpplaceid).first()
            try:
                my_yelpplace = yelpplace(my_yelp_place_record.yelpplace_id, refresh=True)
                my_yelpplace.set_yelpplaceid()
                my_yelpplace.set_placeid(myplacerecord.id)
                my_yelpplace.set_categories()
                my_yelpplace.openinghours_to_db()
            except:
                pass
    db_session.commit()
    flash('updated places')
    return set_config()
      