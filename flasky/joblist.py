#joblist.py

from werkzeug.exceptions import abort
from yelpscrape2 import ys2
import json
from flask.templating import render_template
from sqlalchemy.sql.expression import desc
from models import GooglePlace, JobList, JobResults, Places, SearchCategories, YelpPlace
from flask import (
    Blueprint,
)
from db2 import db_session
from googlescrape2 import gs2
from tar_helper import getapikey

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
    joblist_record = JobList.query.filter(JobList.id == job_id).first()
    mydict = {
        'id': joblist_record.id,
        'address': joblist_record.address,
        'radius': joblist_record.radius,
        'lat': joblist_record.lat,
        'lng': joblist_record.lng,
        'searchcategories': get_search_categories(joblist_record.id)
    }
    placerecords = []
    for placeid in get_places(joblist_record.id):
        placerecord = Places.query.filter(Places.id == placeid).first()
        if placerecord is None:
            continue
        placedict = {
            'id': placeid,
            'placename': placerecord.placename,
            'vicinity': placerecord.vicinity,
            'phonenumber': placerecord.phonenumber
        }
        placerecords.append(placedict)
    mydict['placerecords'] = placerecords
    return render_template('/joblist/jobdisplay.html', job=mydict)

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
