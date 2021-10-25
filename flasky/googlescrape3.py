from flasky.models import GooglePlace, KeyWords, OpeningHours, Places, Reviews, JobResults
import urllib.request
import urllib.parse
import json
from datetime import datetime
import time
from .db2 import db_session
from . import yelpscrape2
from . import zomatoscrape2
from . import tar_helper as helper

'''
What we wanna do?

This version of the scraper will grab all the fields that the user wishes
to collect from the Google Places API.

It will report back with a list of places, and set up a background tasks
to grab the details and stick them in the database.

Once all are collected, they will generate the HTMLreport/xls/cvs report.

I think...

'''

apikey = helper.getapikey('googleapikey')
url = 'https://maps.googleapis.com/maps/api'
business_status_dict = {
    'OPERATIONAL': 1,
    'CLOSED_PERMENANTLY': 0,
    'CLOSED_TEMPORARILY': 2
}
business_status_dict2 = {
    1 : 'OPERATIONAL',
    0 : 'CLOSED_PERMENANTLY',
    2 : 'CLOSED_TEMPORARILY'
}

def get_one_dimensional_list(mylist):
        '''
        Goes through a list looking for lists and adds the contents of the found list to the main list.
        Otherwise, it just returns the contents.
        '''
        output = []
        if type(mylist) is str:
            output.append(mylist)
        else:
            for item in mylist:
                if type(item) is list and type(item) is not str:
                    output.extend(get_one_dimensional_list(item))
                else:
                    output.append(item)
        return output

def street_address_to_lat_lng(street_address):
    '''
    Converts a street address to a latitude/longitude dictionary
    input: string containing street address.
    output: dictionary of lat, lng
    '''

    urldir = "/place/findplacefromtext/json?&inputtype=textquery&fields=geometry&" + apikey
    latlongdict = {
        "lat": "",
        "lng": ""
    }

    urldir = urldir + "&input=" + urllib.parse.quote(street_address)
    data = helper.dataFromURL(url + urldir)
    if len(data['candidates']) == 0:
        raise Exception(
            "Error: streetAddressToLatLong: Couldn't find Address. " + urldir)
    if "error_message" in data:
        raise Exception(
            "Error: streetAddressToLatLong: error_message: " + data['error_message'])
    latlongdict['lat'] = data['candidates'][0]['geometry']['location']['lat']
    latlongdict['lng'] = data['candidates'][0]['geometry']['location']['lng']
    return latlongdict

def find_place(input, is_phone_number=False):
    '''
    Finds a place based on name or phone nymber.
    Returns array of google place IDs.
    '''
    urldir = '/place/findplacefromtext/json?'
    if is_phone_number:
        urldir += '&inputtype=phonenumber'
    else:
        urldir += '&inputtype=textquery'
        urldir += '&fields=place_id&' + apikey
        urldir += '&input=' + urllib.parse.quote(input)
        data = helper.dataFromURL(url + urldir)
    if len(data['candidates']) == 0:
        raise Exception("Error: find_place: couldn't find an entry for your input." + urldir)
    if 'error_message' in data:
            raise Exception('Error: find_place: error message: ' + data['error_message'])
    output = []
    for aresult in data['candidates']:
        output.extend( get_one_dimensional_list(aresult['place_id']))
    return output


def find_place_from_text(input):
    '''
    Finds a place based on name or phone nymber.
    Returns array of google place IDs.
    '''
    urldir = '/place/textsearch/json?'
    urldir += '&fields=formatted_address&' + apikey
    urldir += '&query=' + urllib.parse.quote(input)
    data = helper.dataFromURL(url + urldir)
    if len(data['results']) == 0:
        raise Exception("Error: find_place: couldn't find an entry for your input." + urldir)
    if 'error_message' in data:
        raise Exception('Error: find_place: error message: ' + data['error_message'])
    output = []
    for result in data['results']:
        output.extend(get_one_dimensional_list(result['place_id']))
    return output
        

def nearby_search_one_type(location, radius, mytype, keyword='', minprice=0, maxprice=4):
        '''
        Finds a list of places nearby to the given location in the set radius.
        returns an array of google place ids
        '''
        mylocation = street_address_to_lat_lng(location)
        urldir = '/place/nearbysearch/json?'
        urldir += apikey
        urldir += '&location=' + str(mylocation['lat']) + ',' + str(mylocation['lng'])
        urldir += '&radius=' + radius
        if keyword != '':
            urldir += '&keyword=' + urllib.parse.quote(keyword)
        if mytype != '':
            urldir += '&type=' + mytype
        urldir += '&fields=place_id'
        data = helper.dataFromURL(url + urldir)
        if 'error_message' in data:
            raise Exception('Error: nearby_search: error message: ' + data['error_message'])
        output = []
        for aresult in data['results']:
            output.extend(get_one_dimensional_list(aresult['place_id']))
        if 'next_page_token' in data:
            output.extend(_nearby_search_nextpage(data['next_page_token']))
        return output

def _nearby_search_nextpage(token, sleeptime=3):
    '''
    Gets a list of restaraunt from a next page token
    input: string containing token
    output: list of restaraunt dictionaries
    '''
    urldir = "&".join( ('/place/nearbysearch/json?pagetoken=' + token, apikey,))
    time.sleep(sleeptime)
    data = helper.dataFromURL(url + urldir)
    if 'error_message' in data:
        raise Exception('_nearby_search_nextpage: error_message: ' + data['error_message'])
    output = []
    for aresult in data['results']:
        output.extend(get_one_dimensional_list(aresult['place_id']))
    return output

def _make_street1(address_object):
    '''
    Turns an address object into a single "vicinity string"
    '''
    address_components = ['room', 'floor', 'street_number', 'route']
    address_dict = {}
    street1 = ''
    for address_component in address_components:
        for entry in address_object:
            if address_component in entry['types']:
                address_dict[address_component] = entry['short_name']
    if 'room' in address_dict:
        street1 += address_dict['room'] + '.'
    if 'floor' in address_dict:
        street1 += address_dict['floor'] + '/'
    if 'street_number' in address_dict:
        street1 += address_dict['street_number'] + " "
    if 'route' in address_dict:
        street1 += address_dict['route']
    return street1

def _get_address_component(address_object, componentname):
    return_value = ''
    for entry in address_object:
        if componentname in entry['types']:
            return_value = entry['short_name']
    return return_value


def googleplace_to_db(data):
    aresult = data['result']
    googleplace_id = aresult['place_id']
    business_status = business_status_dict[aresult['business_status']]
    googleplace = GooglePlace.query.filter(GooglePlace.googleplace_id == googleplace_id).first()
    if googleplace is None:
        viewportnelat = aresult['geometry']['viewport']['northeast']['lat']
        viewportnelng = aresult['geometry']['viewport']['northeast']['lng']
        viewportswlat = aresult['geometry']['viewport']['southwest']['lat']
        viewportswlng = aresult['geometry']['viewport']['southwest']['lng']
        lat = aresult['geometry']['location']['lat']
        lng = aresult['geometry']['location']['lng']
        price_level = 0
        if 'price_level' in aresult:
            price_level = aresult['price_level']
        rating = 0
        if 'rating' in aresult:
            rating = aresult['rating']
        user_ratings_total = 0
        if 'user_ratings_total' in aresult:
            user_ratings_total = aresult['user_ratings_total']
        placeurl = aresult['url']
        website = ''
        if 'website' in aresult:
            website = aresult['website']
        
        googleplace = GooglePlace(business_status=business_status, 
            viewportnelat=viewportnelat,
            viewportnelng=viewportnelng, 
            viewportswlat=viewportswlat, 
            viewportswlng=viewportswlng,
            lat=lat, 
            lng=lng, 
            price_level=price_level, 
            rating=rating, 
            user_ratings_total=user_ratings_total,
            googleplace_id=googleplace_id, 
            placeurl=placeurl, 
            website=website)
        db_session.add(googleplace)
        db_session.commit()
    return googleplace.id

def place_to_db(data, googleplaceid):
    aresult = data['result']
    name = aresult['name']
    address_components = aresult['address_components']
    street1 = _make_street1(address_components)
    suburb = _get_address_component(address_components, 'locality')
    restaurantstate = _get_address_component(address_components, 'administrative_area_level_1')
    postcode = _get_address_component(address_components, 'postal_code')
    vicinity = street1 + ', ' + suburb + ' ' + restaurantstate + ', ' + postcode
    phonenumber = '+61000000000'
    if 'international_phone_number' in aresult:
        phonenumber = aresult['international_phone_number'].replace(' ', '')
    
    placerecord = Places.query.filter(Places.googleplaceid == googleplaceid).first()
    if placerecord is None:
        placerecord = Places(placename=name, 
            googleplaceid=googleplaceid, street1=street1, suburb=suburb, 
            vicinity=vicinity, 
            postcode=postcode, 
            placestate=restaurantstate, 
            phonenumber=phonenumber)
        db_session.add(placerecord)
        db_session.commit()
    return placerecord.id

def types_to_db(data, placeid):
    types = data['result']['types']
    for mytype in types:
        helper.add_type_to_place(placeid, mytype)

def _openinghours_to_db(open_hours_ob, placeid):
    oh = OpeningHours.query.filter(OpeningHours.placeid == placeid).first()
    if oh is None:
        oh = OpeningHours(placeid)
    for period in open_hours_ob['periods']:
        #open24 hours
        if (period['open']['day'] == 0) and (period['open']['time'] == '0000') and (period.get('close') is None):
            oh = OpeningHours(placeid, '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359')
            db_session.merge(oh)
            db_session.commit()
            return
        if period['open']['day'] == 0:
            oh.sundayopen = period['open']['time']
        if period['close']['day'] == 0:
            oh.sundayclose = period['close']['time']
        if period['open']['day'] == 1:
            oh.mondayopen = period['open']['time']
        if period['close']['day'] == 1:
            oh.mondayclose = period['close']['time']
        if period['open']['day'] == 2:
            oh.tuesdayopen = period['open']['time']
        if period['close']['day'] == 2:
            oh.tuesdayclose = period['close']['time']
        if period['open']['day'] == 3:
            oh.wednesdayopen = period['open']['time']
        if period['close']['day'] == 3:
            oh.wednesdayclose = period['close']['time']
        if period['open']['day'] == 4:
            oh.thursdayopen = period['open']['time']
        if period['close']['day'] == 4:
            oh.thursdayclose = period['close']['time']
        if period['open']['day'] == 5:
            oh.fridayopen = period['open']['time']
        if period['close']['day'] == 5:
            oh.fridayclose = period['close']['time']
        if period['open']['day'] == 6:
            oh.saturdayopen = period['open']['time']
        if period['close']['day'] == 6:
            oh.saturdayclose = period['close']['time']
        db_session.merge(oh)
        db_session.commit()

def _addgooglereviews (reviews_ob, placeid):
    for review in reviews_ob:
        review = Reviews(placeid, review['rating'], review['text'], 'google')
        db_session.add(review)
    db_session.commit()

def all_to_db(data):
    googleplaceid = googleplace_to_db(data)
    placeid = place_to_db(data, googleplaceid)
    types_to_db(data, placeid)    
    if 'opening_hours' in data['result']:
        _openinghours_to_db(data['result']['opening_hours'], placeid)
    if 'reviews' in data['result']:
        _addgooglereviews(data['result']['reviews'], placeid)
    yelpplaceid = yelpscrape2.get_yelp_place_id(placeid)
    zomplaceid = zomatoscrape2.get_zomato_place_id(placeid)

    googleplace = GooglePlace.query.filter(GooglePlace.id == googleplaceid).first()
    googleplace.placeid = placeid
    googleplace.yelpplaceid = yelpplaceid
    googleplace.zomatoplaceid = zomplaceid
    db_session.commit()
    
    return placeid

def get_place_details(place_ids, refresh=False, onlyaddress=False, job_id=0):
    fields = ['place_id', 'rating', 'address_component', 'business_status', 'geometry', 'name', 'type', 'vicinity', 'url', 'website','international_phone_number', 'opening_hours', 'price_level', 'user_ratings_total']
    if onlyaddress:
        fields = ['address_component']
    for place_id in place_ids:
        go_nogo = GooglePlace.query.filter(GooglePlace.googleplace_id == place_id).first()
        if (go_nogo is not None):
            db_session.add(JobResults(placeid=go_nogo.placeid, jobid=job_id))
            db_session.commit()
            if refresh == False:
                continue
        if type(place_id) is list:
            get_place_details(place_id)
        else:
            urldir = '/place/details/json?'
            urldir = urldir + apikey
            urldir = urldir + '&place_id='
            urldir = urldir + str(place_id)
            urldir = urldir + '&fields='
            urldir = urldir + ','.join(fields)
            ptang = url + urldir
            data = helper.dataFromURL(ptang)
            placeid = all_to_db(data)
            db_session.add(JobResults(placeid=placeid, jobid=job_id))
            db_session.commit()
        if onlyaddress:
            return data['result']['address_components']

    






    