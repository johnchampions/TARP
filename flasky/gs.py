from . import ys
from . import zs
from .models import GooglePlace, Places, OpeningHours, JobResults
from .db import db_session
from .tar_helper import getapikey, dataFromURL, add_type_to_place
from time import sleep
import urllib.parse

apikey = getapikey('googleapikey')
url = 'https://maps.googleapis.com/maps/api'
business_status_dict = {
    'OPERATIONAL': 1,
    'CLOSED_PERMENANTLY': 0,
    'CLOSED_TEMPORARILY': 2
}

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
    data = dataFromURL(url + urldir)
    if len(data['candidates']) == 0:
        raise Exception(
            "Error: streetAddressToLatLong: Couldn't find Address. " + urldir)
    if "error_message" in data:
        raise Exception(
            "Error: streetAddressToLatLong: error_message: " + data['error_message'])
    latlongdict['lat'] = data['candidates'][0]['geometry']['location']['lat']
    latlongdict['lng'] = data['candidates'][0]['geometry']['location']['lng']
    return latlongdict

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


class googlesearch:
    googleidlist = []
    placeidlist = []
    location = dict()

    def __init__(self, location, radius, mytypes, keyword='', minprice=0, maxprice=4 ):
        if location is str:
            self.location = street_address_to_lat_lng(location)
        if len(mytypes) == 0:
            self.googleidlist = self.nearby_search_one_type(radius, '', keyword, minprice, maxprice)
        for mytype in mytypes:
            self.googleidlist.extend(self.nearby_search_one_type(radius, mytype, keyword, minprice, maxprice))
        
    def nearby_search_one_type(self, radius, mytype, keyword='', minprice=0, maxprice=4):
        '''
        Finds a list of places nearby to the given location in the set radius.
        returns an array of google place ids
        '''
        mylocation = street_address_to_lat_lng(self.location)
        urldir = '/place/nearbysearch/json?'
        urldir += apikey
        urldir += '&location=' + str(mylocation['lat']) + ',' + str(mylocation['lng'])
        urldir += '&radius=' + radius
        if keyword != '':
            urldir += '&keyword=' + urllib.parse.quote(keyword)
        if mytype != '':
            urldir += '&type=' + mytype
        urldir += '&fields=place_id'
        data = dataFromURL(url + urldir)
        if 'error_message' in data:
            raise Exception('Error: nearby_search: error message: ' + data['error_message'])
        for aresult in data['results']:
            if aresult['place_id'] not in self.googleidlist:
                self.googleidlist.extend(aresult['place_id'])
        if 'next_page_token' in data:
            self.nearby_search_nextpage(data['next_page_token'])

        
    def nearby_search_nextpage(self, token, sleeptime=3):
        '''
        Gets a list of restaraunt from a next page token
        input: string containing token
        output: list of restaraunt dictionaries
        '''
        urldir = "&".join( ('/place/nearbysearch/json?pagetoken=' + token, apikey,))
        sleep(sleeptime)
        data = dataFromURL(url + urldir)
        if 'error_message' in data:
            raise Exception('_nearby_search_nextpage: error_message: ' + data['error_message'])
        for aresult in data['results']:
            if aresult['place_id'] not in self.googleidlist:
                self.googleidlist.extend(aresult['place_id'])
        if 'next_page_token' in data:
            self.nearby_search_nextpage(data['next_page_token'])
        
    def get_googleidlist(self):
        return self.googleidlist

    def getplaceidlist(self, jobnumber=0):
        if len(self.placeidlist) > 0:
            return self.placeidlist
        for googleid in self.googleidlist:
            mygoogleplace = googleplace(googleid)
            mygoogleplace.get_googleplaceid()
            self.placeidlist.extend(mygoogleplace.get_placeid())
            mygoogleplace.set_categories()
            mygoogleplace.openinghours_to_db()
            mygoogleplace.set_jobnumber(jobnumber)
            myyelpsearch = ys.yelpsearch(mygoogleplace.get_location(), 100, [], keyword=mygoogleplace.get_placename())
            if len(myyelpsearch.get_yelpidlist()) != 0:
                myyelpplace = ys.yelpplace(myyelpsearch.get_yelpidlist()[0])
                myyelpplace.set_placeid(mygoogleplace.get_placeid())
                myyelpplace.set_categories()
            myzomatosearch = zs.zomatosearch(mygoogleplace.get_location(), 100, keyword=mygoogleplace.get_placename())
            if len(myzomatosearch.get_zomatoidlist()) != 0:
                myzomatoplace = zs.zomatoplace(myzomatosearch.get_zomatoidlist()[0])
                myzomatoplace.set_placeid(mygoogleplace.get_placeid())
                myzomatoplace.set_keywords()
        return self.placeidlist


class googleplace:
    placeid = 0
    googleplaceid = 0
    myjson = dict()
    googleid = ""
    jobnumber = int()
    location = dict()
    googleplacerecord = GooglePlace()
    placerecord = Places()

    def __init__(self, googleid):
        self.googleid = googleid
        self.myjson = self.get_place_details()

    def get_place_details(self):
        fields = ['place_id', 'rating', 'address_component', 'business_status', 'geometry', 'name', 'type', 'vicinity', 'url', 'website','international_phone_number', 'opening_hours', 'price_level', 'user_ratings_total']
        urldir = '/place/details/json?'
        urldir = urldir + apikey
        urldir = urldir + '&place_id='
        urldir = urldir + str(self.googleid)
        urldir = urldir + '&fields='
        urldir = urldir + ','.join(fields)
        fullurl = url + urldir
        self.myjson = dataFromURL(fullurl)

    def get_googleplaceid(self):
        if self.googleplaceid == 0:
            self.set_googleplaceid()
        return self.googleplaceid
    
    def set_googleplaceid(self):
        self.googleplacerecord = GooglePlace.query.filter(GooglePlace.googleplace_id == self.googleid).first()
        if self.googleplacerecord is not None:
            return self.googleplacerecord.id
        aresult = self.myjson['result']
        business_status = business_status_dict[aresult['business_status']]
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
        
        self.googleplacerecord = GooglePlace(business_status=business_status, 
            viewportnelat=viewportnelat,
            viewportnelng=viewportnelng, 
            viewportswlat=viewportswlat, 
            viewportswlng=viewportswlng,
            lat=lat, 
            lng=lng, 
            price_level=price_level, 
            rating=rating, 
            user_ratings_total=user_ratings_total,
            googleplace_id=self.googleid, 
            placeurl=placeurl, 
            website=website)
        db_session.add(self.googleplacerecord)
        db_session.commit()
        return self.googleplacerecord.id

    def get_placeid(self):
        if self.placeid > 0:
            return self.placeid
        if self.googleplacerecord.placeid is None:
            self.set_placeid()
        return self.placeid

    def set_placeid(self, placeid=0):
        self.placerecord = Places.query.filter(Places.id == placeid).first()
        if self.placerecord is None:
            aresult = self.myjson['result']
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
            self.placerecord = Places(placename=name, 
                googleplaceid=self.get_googleplaceid(), 
                street1=street1, suburb=suburb, 
                vicinity=vicinity, 
                postcode=postcode, 
                placestate=restaurantstate, 
                phonenumber=phonenumber)
            db_session.add(self.placerecord)
            db_session.commit()
            self.placeid = self.placerecord.id            
        else:
            self.placeid = placeid
        self.placerecord.googleplaceid = self.get_googleplaceid()
        self.googleplacerecord.placeid = self.placeid
        db_session.commit()


    def set_categories(self):
        types = self.myjson['result']['types']
        for mytype in types:
            add_type_to_place(self.get_placeid(), mytype)

    def openinghours_to_db(self):
        open_hours_ob = self.myjson['opening_hours']
        oh = OpeningHours.query.filter(OpeningHours.placeid == self.get_placeid()).first()
        if oh is None:
            oh = OpeningHours(self.placeid)
        for period in open_hours_ob['periods']:
            #open24 hours
            if (period['open']['day'] == 0) and (period['open']['time'] == '0000') and (period.get('close') is None):
                oh = OpeningHours(self.placeid, '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359')
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
        
    def get_placename(self):
        return self.placerecord.placename

    def set_yelpplace(self, yelpplaceid):
        self.placerecord.yelpplaceid = yelpplaceid

    def set_jobnumber(self, jobnumber):
        db_session.add(JobResults(placeid=self.get_placeid(), jobid=jobnumber))
        db_session.commit()

    def get_location(self):
        location = dict(lat = self.googleplacerecord.lat,
            lng = self.googleplacerecord.lng)
        return location
    


