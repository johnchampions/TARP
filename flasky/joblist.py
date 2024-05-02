from sqlalchemy import outparam
from werkzeug.exceptions import abort
import json
from flask.templating import render_template
from sqlalchemy.sql.expression import desc
from flasky.models import GooglePlace, JobList, JobResults, Places, SearchCategories
from flask import Blueprint
import time

from . import gs

bp = Blueprint('joblist', __name__, url_prefix='/joblist')

@bp.route('/', methods=('GET',))
@bp.route('', methods=('GET',))
@bp.route('/joblist', methods=('GET',))
def search_for_joblist(getall=False):
    output = []
    joblistrecords = JobList.query.all()
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
    joblist_record = JobList.query.filter(JobList.id == job_id).first()

    mydict = {
        'id': joblist_record.id,
        'address': joblist_record.address,
        'radius': joblist_record.radius,
        'lat': joblist_record.lat,
        'lng': joblist_record.lng,
        'searchcategories': get_search_categories(joblist_record.id),
        'roughcount': joblist_record.roughcount,
        'finished': is_finished(joblist_record)
    }
    placerecords = get_restaurantlist(job_id)
    placerecords=placerecords
    return render_template('/joblist/jobdisplay.html', job=mydict, placerecords=placerecords)

def is_finished(joblist_record):
    return (joblist_record.googleplugin == 0 or joblist_record.googlecomplete)  and  (joblist_record.yelpplugin == 0 or joblist_record.yelpcomplete) and (joblist_record.zomatoplugin == 0 or joblist_record.zomatocomplete)

def update_restaurants(job_id):
    now = time.time()
    timeout = now + 360.0
    while time.time() < timeout:
        placerecords = get_restaurantlist(job_id)
        render_template('/joblist/restaurantlist.html', placerecords=placerecords)
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
    for id in idlist:
        placerecord = Places.query.filter(Places.id == id).first()
        if placerecord.googleplaceid is not None:
            gpid = GooglePlace.query.filter(GooglePlace.placeid == id).first().googleplace_id
            gs.get_place_details((gpid,), refresh=True)

def get_restaurantlist(jobid=0):
    output = []
    myrecords = JobResults.query.filter(JobResults.jobid == jobid).all()
    for record in myrecords:
        myplace = Places.query.filter(Places.id == record.placeid).first()
        if myplace is not None:
            output.append(myplace.__dict__)
    return output

def get_incomplete_zomato_jobs():
    output = []
    myJoblist = JobList.query.filter(JobList.zomatoplugin > 0, JobList.zomatocomplete  == 0).all()
    for jobby in myJoblist:
        output.append(jobby.id)
    return output

@bp.route('/zomjob/<key>', methods=('GET',))
def get_zomato_jobs(key):
    if key != 'Z':
        return '{"error": "Insufficient beer in diet."}'
    job_list = get_incomplete_zomato_jobs()
    jobs_avail = len(job_list) > 0
    mydict = {'jobsAvailable': jobs_avail,
        'joblist': job_list}
    return json.dumps(mydict)