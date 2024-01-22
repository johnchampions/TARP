import flask_user
import threading
import io
import json
from flask_user.decorators import login_required
from werkzeug.utils import send_file
from flask import (
    Blueprint,
    flash,
    render_template,
    request,
    redirect,
    send_file
)
from werkzeug.exceptions import abort
from json_excel_converter import Converter
from json_excel_converter.xlsx import Writer

from .gs import googlesearch, street_address_to_lat_lng
from . import reports
from .joblist import display_job
from .models import JobList, KeyWords, Places, PostCode, SearchCategories
from . import tar_helper as helper
from .db import db_session


bp = Blueprint('tar', __name__, url_prefix='/tar')

@bp.route('/latlong', methods=('GET', 'POST'))
@login_required
def latlong():
    if request.method == 'POST':
        address = request.form['address']
        error = None
        if not address:
            error = 'An address is required'
        try:
            latlong = street_address_to_lat_lng(address)
        except Exception as e:
            error = str(e)
        if error is None:
            return render_template('tar/latlong.html', latlong=latlong)
        flash(error)
    return render_template('tar/search.html')


@bp.route('/keyword', methods=('GET', 'POST'))
@login_required
def keyword_search():
    if request.method == 'POST':
        error = None
        keywords = request.form['keywords']
        if not keywords:
            error = 'You really need something to search for.'
        keywords_list = keywords.split()
        keywords_list.append('restaurant')
        if len(keywords_list) == 0:
            error = 'You really need a word to search for.'
        restaurantlist = []
        for keyword in keywords_list:
            keywordslist = KeyWords.query.filter(KeyWords.placetype == keyword)
            for keyword in keywordslist:
                if keyword.placeid not in restaurantlist:
                    restaurantlist.append(keyword.placeid)
        places = Places.query.filter(Places.id in restaurantlist)
        if places is None:
            error = 'Unsuccessful search.  I''m not that bright.'
        recordlist = []
        for place in places:
            placedict = {
                'id' : place.id,
                'name' : place.placename,
                'postcode' : place.postcode
            }
            recordlist.append(placedict)
        if error is None:
            return render_template('tar/keywordresults.html', keywords=keywords, recordlist=recordlist)
        flash(error)
    return render_template('tar/keywordsearch.html')


@bp.route('/restaurants/<int:id>', methods=('GET',))
@login_required
def get_restaurant(id):
    place = Places.query.filter(Places.id == id).first()
    if place is None:
        abort(404,  f"Restaurant id {id} doesn't exist.")
    
    record = {
        'id': place.id,
        'placename': place.placename,
        'vicinity': place.vicinity,
        'suburb': place.suburb,
        'postcode' : place.postcode,
        'state' : place.placestate,
        'phonenumber' : place.phonenumber
    }
    record.update(helper.get_openinghours(id))
    record['urls'] = helper.get_urls(id)
    mykeywords = KeyWords.query.filter( KeyWords.placeid == id).all()
    keywords =[]
    for keyword in mykeywords:
        if keyword.placetype not in keywords:
            keywords.append(keyword.placetype)
    record['keywords'] = keywords
    return render_template('/tar/restaurant.html', record=record)

@bp.route('/postcodes', methods=('GET', 'POST',))
@login_required
def search_postcodes():
    if request.method == 'POST':
        postcode = request.form['postcode']
        return render_template('/tar/postcode.html', record=get_postcode(postcode), restaurants=get_places_in_postcode(postcode))
    return render_template('tar/postcodesearch.html')

def get_postcode(postcode):
    locality = []
    sa2 = []
    postcode_records = PostCode.query.filter(PostCode.postcode == int(postcode)).all()
    if postcode_records is None:
        abort(404, f"Postcode id {postcode} doesn't exist.")
    for postcode_record in postcode_records:
        locality.append(postcode_record.Locality)
        sa2.append(postcode_record.sa2)
        postcode_record = { 'postcode': postcode,
            'postcodestate': postcode_record.postcodestate}
    postcode_record['locality'] = locality
    postcode_record['sa2'] = sa2
    return postcode_record

def get_places_in_postcode(postcode):
    restaurant_records = Places.query.filter(Places.postcode == postcode).all()
    restaurantlist = []
    for restaurant_record in restaurant_records:
        restaurant_dict = {
            'id': restaurant_record.id,
            'restaurantname': restaurant_record.placename,
            'street1': restaurant_record.street1,
        }
        restaurantlist.append(restaurant_dict)
    return restaurantlist

@bp.route('/postcodes/<string:postcode>', methods=('GET',))
@login_required
def get_postcode_from_url(postcode):
    return render_template('/tar/postcode.html', record=get_postcode(postcode), restaurants=get_places_in_postcode(postcode))


@bp.route('/search', methods=('GET', 'POST',))
@login_required
def search():
    if request.method == 'POST':
        error = None
        gt = None
        job_dict = {}
        address = request.form['address']
        radius = request.form['radius']
        if not address:
            error = 'An address is required.'
        if not radius:
            error = 'A radius is required.'
        job_dict['address'] = address
        job_dict['radius'] = radius
        job_dict['placelist'] = []
        job_dict['roughcount'] = 0
        myjob = JobList(address=request.form['address'], radius=request.form['radius'], roughcount=0, userid=flask_user.current_user.id)
        db_session.add(myjob)
        db_session.commit()
        jobid = myjob.id
        try:
            latlong = street_address_to_lat_lng(address)
        except:
            error = 'Could not find address'
            flash(error)
            return render_template('/tar/googlesearch.html', recordlist=helper.get_google_supported_types())
        job_dict['lat'] = latlong['lat']
        job_dict['lng'] = latlong['lng']
        myjob.lat = latlong['lat'],
        myjob.lng = latlong['lng']
        minprice = request.form['minprice']
        maxprice = request.form['maxprice']
        myjob.maxprice = request.form['minprice']
        myjob.maxprice = request.form['minprice']

        if request.form.get('googleplugin') is not None:
            googleplacelist = ()
            types = request.form.getlist('type')
            keyword = request.form['keyword']
            if len(types) == 0:
                if keyword == '':
                    error = 'A google type or a keyword is required'
            else:    
                googleplacelist = []
                if len(types) > 0:
                    job_dict['types'] = types
                    for mytype in types:
                        mycategory = SearchCategories(jobid=jobid, category=mytype, plugin='googletype')
                        db_session.add(mycategory)
                    try:
                        mygooglesearch = googlesearch(address, radius, types, keyword, minprice, maxprice)
                        googleplacelist = mygooglesearch.get_googleidlist()
                        mygooglesearch.getplaceidlist(jobid)
                    except Exception as e:
                        error = str(e)
                elif keyword != '':
                    job_dict['keyword'] = keyword
                    mycategory = SearchCategories(jobid=jobid, category=keyword, plugin='googlekeyword')
                    db_session.add(mycategory)
                    try:
                        mygooglesearch = googlesearch(address, radius, [], keyword, minprice, maxprice)
                        googleplacelist = mygooglesearch.get_googleidlist()
                        gt = threading.Thread(target=mygooglesearch.getplaceidlist, kwargs={'jobnumber':jobid})
                        gt.start()
                        job_dict['roughcount'] = job_dict['roughcount'] + len(googleplacelist)
                    except Exception as e:
                        error = str(e)
                job_dict['roughcount'] = job_dict['roughcount'] + len(googleplacelist)
                myjob.googleplugin = len(googleplacelist)
                myjob.googlecomplete = False

        myjob.roughcount=job_dict['roughcount']
        db_session.commit()
        try:
            if error is None:
                return redirect('/joblist/jobdisplay/' + str(jobid))
            else:
                flash(error)
                return render_template('/tar/googlesearch.html', recordlist=helper.get_google_supported_types())
        finally:
            pass
    else: 
        return render_template('/tar/googlesearch.html', recordlist=helper.get_google_supported_types())


@bp.route('/downloads/<path:path_to_file>')
@login_required
def get_xls_report(path_to_file):
    error = None
    try: 
        jobnumber = int(path_to_file.split('.')[0].split('_')[1])
        jobtype = str(path_to_file.split('.')[0].split('_')[0])
        jobformat = str(path_to_file.split('.')[1])
    except:
        error = 'Could not get that file.'
        abort(404,error)
    
    job = JobList.query.filter(JobList.id == jobnumber).first()
    if job is None:
        error = 'Could not find that files job.'
    if error:
        abort(404,error)
    
    proxyIO = io.StringIO()
    mem = io.BytesIO()
    #TODO: Fix this bit...
    if jobtype == 'job':
        if jobformat == 'json':
            proxyIO.write(reports.create_job_json(jobnumber))
        elif jobformat == 'xlsx':
            data = (json.load(reports.create_job_json(jobnumber)))
            converter = Converter()
            converter.convert(data, Writer(mem))
    elif jobtype == 'tarreport':
        try:
            data = reports.tarreport(jobnumber).create_tar_report()
        except Exception as e:
            abort(404, e)
        converter = Converter()
        converter.convert(data, Writer(mem))
    elif jobtype == 'RawReport':
        data = reports.uglyreport(jobnumber).create_report()
        converter = Converter()
        converter.convert(data, Writer(mem))
    elif jobtype == 'NewTarReport':
        data = reports.new_tar_report(jobnumber).create_report()
        converter = Converter()
        converter.convert(data, Writer(mem))
    mem.seek(0)
    myreturnfile = send_file(mem, download_name=path_to_file,
        as_attachment=True)
    if jobformat == 'csv':
        myreturnfile.mimetype = 'text/csv'
    elif jobformat == 'json':
        myreturnfile.mimetype = 'application/json'
    elif jobformat == 'xlsx':
        myreturnfile == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return myreturnfile