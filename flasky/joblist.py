from flask.cli import with_appcontext
from werkzeug.exceptions import abort
from flasky.yelpscrape2 import ys2
import json
from flask.templating import render_template
from sqlalchemy.sql.expression import desc
from flasky.models import GooglePlace, JobList, JobResults, Places, SearchCategories, YelpPlace
from flask import (
    Blueprint, current_app
)
from flasky.db2 import db_session
from flasky.googlescrape2 import gs2
from flasky.tar_helper import getapikey
import threading
import time
import application

bp = Blueprint('joblist', __name__, url_prefix='/joblist')


@bp.route('/', methods=('GET',))
@bp.route('', methods=('GET',))
@bp.route('/joblist2', methods=('GET',))
def search_for_joblist():
    output = []
    joblistrecords = JobList.query.order_by(desc(JobList.id)).all()
    for joblistrecord in joblistrecords:
        mydict = {'id': joblistrecord.id,
            'address': joblistrecord.address,
            'radius': joblistrecord.radius,
            'types': get_search_categories(joblistrecord.id)
        }
        output.append(mydict)
    return render_template('/joblist/joblist.html', records=output)

def get_search_categories(jobid):
    searchcategories = []
    searchcategoriesrecords = SearchCategories.query.filter(SearchCategories.jobid == jobid).all()
    for record in searchcategoriesrecords:
        searchcategories.append(record.category)
    return searchcategories

def get_places(jobid):
    output = []
    jobresultrecords = JobResults.query.filter(JobResults.jobid == jobid).all()
    for jobresult in jobresultrecords:
        output.append(jobresult.placeid)
    return output



@bp.route('/jobdisplay/<int:job_id>', methods=('GET',))
def display_job(job_id):
    threading.Thread(target=update_restaurants, args=(job_id,)).start()
    joblist_record = JobList.query.filter(JobList.id == job_id).first()
    mydict = {
        'id': joblist_record.id,
        'address': joblist_record.address,
        'radius': joblist_record.radius,
        'lat': joblist_record.lat,
        'lng': joblist_record.lng,
        'searchcategories': get_search_categories(joblist_record.id),
        'roughcount': joblist_record.roughcount
    }
    return render_template('/joblist/jobdisplay.html', job=mydict)

def update_restaurants(job_id):
    with application.application.app_context():
        now = time.time()
        timeout = now + 360.0
        while time.time() < timeout:
            placerecords = get_restaurantlist(job_id)
            application.turbo.push(application.turbo.replace(render_template('/joblist/restaurantlist.html', placerecords=placerecords), 'load'))
            time.sleep(5)

@bp.route('/jobrefresh/<int:job_id>', methods=('GET',))
def refresh_job_places(job_id):
    joblist_record = JobList.query.filter(JobList.id == job_id).first()
    if joblist_record is None:
        abort(404,  f"Search id {job_id} doesn't exist.")
    mydict = json.loads(joblist_record.jobjson)
    refresh_places(mydict['placelist'])
    return display_job(job_id)

def refresh_place(id):
    refresh_places((id,))
    
def refresh_places(idlist):
    gs = gs2(getapikey('googleapikey'))
    ys = ys2(getapikey('yelpapikey'))
    for id in idlist:
        placerecord = Places.query.filter(Places.id == id).first()
        if placerecord.googleplaceid is not None:
            gpid = GooglePlace.query.filter(GooglePlace.placeid == id).first().googleplace_id
            gs.get_place_details((gpid,), refresh=True)
        if placerecord.yelpplaceid is not None:
            ysid = YelpPlace.query.filter(YelpPlace.placeid == id).first().yelpplace_id
            ys.get_place_details((ysid,), refresh=True)

def get_restaurantlist(jobid=0):
    output = []
    myrecords = JobResults.query.filter(JobResults.jobid == jobid).all()
    for record in myrecords:
        myplace = Places.query.filter(Places.id == record.placeid).first()
        if myplace is not None:
            output.append(myplace.__dict__)
    return output
