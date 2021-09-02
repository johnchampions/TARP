from flasky.zomatoscrape2 import zs2
from flask import (
    Blueprint,
    flash,
    render_template,
    request,
)
import flask
from werkzeug.exceptions import abort
import flasky.reports
from flasky.auth import login_required
from flasky.joblist import display_job
from flasky.googlescrape2 import gs2
from flasky.yelpscrape2 import ys2
import flasky.tar_helper as helper
import io
import json
from flasky.models import JobList, JobResults, KeyWords, Places, PostCode, SearchCategories
from json_excel_converter import Converter
from json_excel_converter.xlsx import Writer
from flasky.db2 import db_session
from threading import Thread

bp = Blueprint('tar', __name__, url_prefix='/tar')

@bp.route('/latlong', methods=('GET', 'POST'))
def latlong():
    if request.method == 'POST':
        address = request.form['address']
        myGoogleScrape = gs2(helper.getapikey('googleapikey'))
        error = None
        if not address:
            error = 'An address is required'
        try:
            latlong = myGoogleScrape.streetAddressToLatLong(address)
        except Exception as e:
            error = str(e)
        if error is None:
            return render_template('tar/latlong.html', latlong=latlong)
        flash(error)
    return render_template('tar/search.html')


@bp.route('/keyword', methods=('GET', 'POST'))
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
def get_postcode_from_url(postcode):
    return render_template('/tar/postcode.html', record=get_postcode(postcode), restaurants=get_places_in_postcode(postcode))


@bp.route('/search', methods=('GET', 'POST',))
def search():
    if request.method == 'POST':
        error = None
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
        myjob = JobList(address=request.form['address'], radius=request.form['radius'], roughcount=0)
        db_session.add(myjob)
        db_session.commit()
        jobid = myjob.id
        gs = gs2(helper.getapikey('googleapikey'))
        try:
            latlong = gs.street_address_to_lat_lng(address)
        except:
            error = 'Could not find address'
            flash(error)
            return render_template('/tar/googlesearch.html')
        job_dict['lat'] = latlong['lat']
        job_dict['lng'] = latlong['lng']
        myjob.lat = latlong['lat'],
        myjob.lng = latlong['lng']
        
        if request.form.get('googleplugin') is not None:
            googleplacelist = ()
            types = request.form.getlist('type')
            keyword = request.form['keyword']
            if len(types) == 0:
                if keyword == '':
                    error = 'A google type or a keyword is required'
            else:    
                minprice = request.form['minprice']
                maxprice = request.form['maxprice']
                myjob.maxprice = request.form['minprice']
                myjob.maxprice = request.form['minprice']
                googleplacelist = []
                if len(types) > 0:
                    job_dict['types'] = types
                    for mytype in types:
                        mycategory = SearchCategories(jobid=jobid, category=mytype, plugin='googletype')
                        db_session.add(mycategory)
                        try:
                            googleplacelist.extend(gs.nearby_search_one_type(address, radius, mytype, keyword=keyword,  minprice=minprice, maxprice=maxprice))        
                        except Exception as e:
                            error = str(e)
                elif keyword != '':
                    job_dict['keyword'] = keyword
                    mycategory = SearchCategories(jobid=jobid, category=keyword, plugin='googlekeyword')
                    db_session.add(mycategory)
                    googleplacelist.extend(gs.nearby_search_one_type(address, radius, mytype='' , keyword=keyword,  minprice=minprice, maxprice=maxprice))   
            gres = []
            for i in googleplacelist:
                if i not in gres:
                    gres.append(i)
            Thread(target=gs.get_place_details, kwargs={'place_ids':gres, 'job_id' : jobid}).start()
            job_dict['roughcount'] = job_dict['roughcount'] + len(googleplacelist)

        if request.form.get('yelpplugin'):
            myys = ys2(helper.getapikey('yelpapikey'))
            categories = request.form.getlist('categories')
            term = request.form['keyword']
            if (not categories) and (term == ''):
                error = 'A yelp category or a keyword is required'
            else:
                minprice = request.form['minprice']
                maxprice = request.form['maxprice']
                myjob.maxprice = request.form['minprice']
                myjob.maxprice = request.form['minprice']
            if len(categories) > 0:
                job_dict['categories'] = categories
                for category in categories:
                    myrecord = SearchCategories(jobid=jobid, category=category, plugin='yelpcategory')
                    db_session.add(myrecord)
            if term != '':
                job_dict['keyword'] = term
                myrecord = SearchCategories(jobid=jobid, category=term, plugin='yelpkeyword')
                db_session.add(myrecord)
            yelpids = myys.nearby_places(latlong, radius, categories, minprice=minprice, maxprice=maxprice, keyword=term)
            
            yt = Thread(target=myys.get_place_details, kwargs={'place_ids': yelpids, 'job_id':jobid})
            yt.start()
            job_dict['roughcount'] = job_dict['roughcount'] + len(yelpids)
        
        if request.form.get('zomatoplugin'):
            myzs = zs2()
            term = request.form['keyword']
            if term != '':
                job_dict['keyword'] = term
                myrecord = SearchCategories(jobid=jobid, category=term, plugin='zomatokeyword')
            else:
                myrecord = SearchCategories(jobid=jobid, plugin='zomatosearch')
            zomids = myzs.nearby_places(job_dict, radius, term)
            job_dict['roughcount'] = job_dict['roughcount'] + len(zomids)
            Thread(target=myzs.linklist_to_db, kwargs={'linklist':zomids, 'job_id': jobid}).start()
            
        myjob.roughcount=job_dict['roughcount']
        db_session.commit()
        if job_dict['roughcount'] == 0:
            error = 'That search had no hits.'
       
        if error is None:
            return  flasky.joblist.display_job(myjob.id)
        flash(error)
    return render_template('/tar/googlesearch.html')


@bp.route('/downloads/<path:path_to_file>')
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
            proxyIO.write(flasky.reports.create_job_json(jobnumber))
        elif jobformat == 'xlsx':
            data = (json.load(flasky.reports.create_job_json(jobnumber)))
            converter = Converter()
            converter.convert(data, Writer(mem))
    elif jobtype == 'tarreport':
        data = flasky.reports.tarreport(jobnumber).create_tar_report()
        converter = Converter()
        converter.convert(data, Writer(mem))
    elif jobtype == 'uglyreport':
        data = flasky.reports.uglyreport(jobnumber).create_report()
        converter = Converter()
        converter.convert(data, Writer(mem))
    mem.seek(0)
    myreturnfile = flask.send_file(mem, attachment_filename=path_to_file,
        as_attachment=True, cache_timeout=0)
    if jobformat == 'csv':
        myreturnfile.mimetype = 'text/csv'
    elif jobformat == 'json':
        myreturnfile.mimetype = 'application/json'
    elif jobformat == 'xlsx':
        myreturnfile == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return myreturnfile