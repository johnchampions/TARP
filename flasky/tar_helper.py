from fuzzywuzzy import process, fuzz
import datetime
import urllib.request
import json
from flasky.db2 import db_session
from flasky.models import ConfigKeys, GooglePlace, JobList, OpeningHours, Places, YelpPlace, ZomatoPlace


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
    ck = ConfigKeys.query.filter(ConfigKeys.keyname == 'blacklistcategories').first()
    output = ck.keyvalue.split(',')
    return output

def removeRepeats(listOfDictionaries):
    """Removes double entries from our list of restaraunts.
    input: list of dictionaries
    output: slightly shorter list of dictionaries."""
    
    myResult = []
    myIds = []
    for myDict in listOfDictionaries:
        if not myDict["id"] in myIds:
            myResult.append(myDict)
            myIds.append(myDict["id"])
    return myResult

def remove_repeats_across_lists(firstlist, secondlist):
    """Combines lists into one giant list and amalgamates scores and such
    """
    if len(firstlist) == 0:
        return secondlist
    if len(secondlist) == 0:
        return firstlist

    biglistofrestarauntnames = []
    returnlist = []
    for myrecord in firstlist:
        biglistofrestarauntnames.append(myrecord["name"])
    for myrecord in secondlist:
        (highestname, score) = process.extractOne(myrecord["name"], biglistofrestarauntnames)
        if score > 80:
            myindex = biglistofrestarauntnames.index(highestname)
            returnlist.append(smooshrecords(firstlist[myindex], myrecord))
        else:
            returnlist.append(myrecord)
    return returnlist

def smooshrecords(dict1, dict2):
    """Combines two restaraunt records into one.  Averages out price_level
    and rating accross the two dictionaries."""
    returndict = dict1
    pricelevel = int(((dict1['price_level'] * dict1['total_user_ratings']) + (dict2['price_level'] * dict2['total_user_ratings'])) / (dict1['total_user_ratings'] + dict2['total_user_ratings']))
    returndict.update({'price_level': pricelevel})
    rating = int(((dict1['rating'] * dict1['total_user_ratings']) + (dict2['rating'] * dict2['total_user_ratings'])) / (dict1['total_user_ratings'] + dict2['total_user_ratings']))
    returndict.update({'rating': rating})
    userratings = dict1['total_user_ratings'] + dict2['total_user_ratings']
    returndict.update({'total_user_ratings': userratings})
    returndict.update({'type': dict1['type'] + "," + dict2['type']})
    return returndict

'''
def get_state_from_postcode(postcode):
    db = get_db()
    retval = db.execute(
        'SELECT postcodestate FROM postcode WHERE postcode = ?', (postcode,)
    ).fetchone()[0]
    if retval is None:
        return ""
    return retval
'''

def dataFromURL(fullURL):
    """Grabs a file off the internet.
    input: full URL of the file
    output: a string containing the server response, usually a file
    """
    request = urllib.request.Request(fullURL)
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        raise Exception("Unexpected Error: " + fullURL + " : " + e.reason)
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
    

def yelpplacelist_to_placelist(yelpplacelist):
    output = []
    for yelpplace in yelpplacelist:
        yelpplacerecord = YelpPlace.query.filter(YelpPlace.yelpplace_id == yelpplace).first()
        if yelpplacerecord is not None:
            output.append(yelpplacerecord.placeid)
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
    