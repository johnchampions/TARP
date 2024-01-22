import urllib.request
import json
from .db import db_session
from flasky.models import ConfigKeys, CuisineList, GooglePlace, JobList, OpeningHours, Places, YelpPlace, ZomatoPlace, KeyWords, PostCode, GoogleSupportedTypes
import openlocationcode


def getapikey(key_name):
    ck = ConfigKeys.query.filter(ConfigKeys.keyname == key_name).first()
    return ck.keyvalue

def getapis():
    possible_apis = ('google', 'yelp', )
    my_output = []
    for api in possible_apis:
        if getapikey(api + 'apikey') is not None:
            my_output.append(api)
    return my_output

def get_blacklist():
    my_records = CuisineList.query.filter(CuisineList.blacklist == True).all()
    output = []
    for record in my_records:
        output.append(record.placetype)
    return output

def add_type_to_place(placeid, mytype):
    if placeid == 0:
        return
    blacklist = get_blacklist()
    if mytype in blacklist:
        return
    my_type_record = KeyWords.query.filter(KeyWords.placeid == placeid, KeyWords.placetype == mytype).first()
    if my_type_record is None:
        keyword = KeyWords(placeid, mytype)
        db_session.add(keyword)
    my_cuisine_record = CuisineList.query.filter(CuisineList.placetype == mytype).first()
    if my_cuisine_record is None:
        my_cuisine_record = CuisineList(mytype, cuisine=True)
        db_session.add(my_cuisine_record)
    db_session.commit()
    

def get_location_from_placeid(placeid):
    myplace = Places.query.filter(Places.id == placeid).first()
    if myplace is None:
        raise Exception(f"Place {placeid} does not exist.")
    if myplace.googleplaceid is not None:
        myp = GooglePlace.query.filter(GooglePlace.id == myplace.googleplaceid).first()
    else:
        from . import gs
        try:
            return gs.street_address_to_lat_lng(myplace.vicinity)
        except:
            return dict(lat = 0.0, lng = 0.0)
    if (myp.lat is None) or (myp.lng is None):
        return dict(lat = 0.0, lng = 0.0)
    return dict(lat = myp.lat, lng = myp.lng)

def get_state_from_postcode(postcode):
    record = PostCode.query.filter(PostCode.postcode == int(postcode)).first()
    return record.postcodestate
    
def get_pluscode_from_placeid(placeid):
    my_location = get_location_from_placeid(placeid)
    return openlocationcode.encode(my_location['lat'], my_location['lng'])


def dataFromURL(fullURL):
    """Grabs a file off the internet.
    input: full URL of the file
    output: a string containing the server response, usually a file
    """
    request = urllib.request.Request(fullURL)
    try:
        response = urllib.request.urlopen(request, timeout=10)
    except urllib.error.URLError as e:
        raise Exception("Unexpected Error: " + fullURL)
    jsonData = json.loads(response.read())
    return jsonData

def make_job(jobdict):
    joblist = JobList(json.dumps(jobdict))
    db_session.add(joblist)
    db_session.commit()
    return joblist.id
    

def googleplacelist_to_placelist(googleplacelist):
    output = []
    for googleplace in googleplacelist:
        googleplacerecord = GooglePlace.query.filter(GooglePlace.googleplace_id == googleplace).first()
        if googleplacerecord is not None:
            output.append(googleplacerecord.placeid)
    return output
    
def listofplaces_to_listofdict(listofplaces):
    output = []
    for place in listofplaces:
        if type(place) is list:
            output.extend(listofplaces_to_listofdict(place))
        else:
            placerecord = Places.query.filter(Places.id == place)
            mydict = {
                'placename': placerecord.placename,
                'vicinity': placerecord.vicinity
            }
            output.append(mydict)
    return output

def get_openinghours(placeid):
    myopeninghoursrecord = OpeningHours.query.filter(OpeningHours.placeid == placeid).first()
    if myopeninghoursrecord is None:
        return {}
    mydict = myopeninghoursrecord.__dict__
    del mydict['id']
    return mydict

def get_reviews(placeid):
    output = []
    gr = GooglePlace.query.filter(GooglePlace.placeid == placeid).first()
    if gr is not None:
        grdict = {
            'source': 'Google',
            'price': gr.price_level,
            'rating': gr.rating,
            'reviews': gr.user_ratings_total
        }
        output.append(grdict)
    yr = YelpPlace.query.filter(YelpPlace.placeid == placeid).first()
    if yr is not None:
        yrdict = {
            'source': 'Yelp',
            'price': yr.price_level,
            'rating': yr.rating,
            'reviews': yr.user_ratings_total
        }
        output.append(yrdict)
    return output

def get_urls(placeid):
    output = []
    gr = GooglePlace.query.filter(GooglePlace.placeid == placeid).first()
    if gr is not None:
        for url in (gr.placeurl, gr.website):
            if url is not None:
                output.append(url)
    yr = YelpPlace.query.filter(YelpPlace.placeid == placeid).first()
    if (yr is not None) and (yr.website is not None):
        output.append(yr.website)
    zr = ZomatoPlace.query.filter(ZomatoPlace.placeid == placeid).first()
    if (zr is not None) and (zr.website is not None):
        output.append(zr.website)
    return output

def add_keywords(keywordlist, place_id):
    if keywordlist is str:
        myrecord = KeyWords(placeid=place_id, placetype = keywordlist)
        db_session.add(myrecord)
    else:
        for keyword in keywordlist:
            myrecord = KeyWords(placeid=place_id, placetype=keyword)
            db_session.add(myrecord)
    db_session.commit()


def make_timing_string(placeid):
    dayslist = ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',)
    oclist = ('open', 'close',)
    timings = OpeningHours.query.filter(OpeningHours.placeid == placeid).first()
    if timings is None:
        return ''
    output = ''
    for day in dayslist:
        for oc in oclist:
            name = day + oc
            exec ("%s" % (name,))
            if timings.name is None:
                foo = ''
            else:
                foo = timings.name
            if oc == 'open':
                output += day + ' ' + foo + ' - '
            else:
                output += foo + ','
    return output

def get_google_supported_types();
    output = GoogleSupportedTypes.query.all()
    return output