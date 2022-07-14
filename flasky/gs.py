from queue import Queue
from . import ys
from . import zs
from .models import GooglePlace, JobList, Places, OpeningHours, JobResults
from .db import db_session
from .tar_helper import getapikey, dataFromURL, add_type_to_place
from time import sleep
import urllib.parse
from openlocationcode import openlocationcode
import threading

apikey = getapikey('googleapikey')
url = 'https://maps.googleapis.com/maps/api'
business_status_dict = {
    'OPERATIONAL': 1,
    'CLOSED_PERMANENTLY': 0,
    'CLOSED_TEMPORARILY': 2
}

typeq = Queue()
q = Queue()

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
    
    #typeq = Queue()

    def __init__(self, location, radius, mytypes, keyword='', minprice=0, maxprice=4 ):
        if type(location) is str:
            self.location = street_address_to_lat_lng(location)
        else:
            self.location = location
        self.googleidlist = []
        self.placeidlist = []
        if len(mytypes) == 0:
            self.nearby_search_one_type(radius, '', keyword, minprice, maxprice)
            return
        for i in range(5):
            worker = threading.Thread(target=self._nearby_search_one_type, args=(typeq,))
            worker.setDaemon(False)
            worker.start()
        for mytype in mytypes:
            typeq.put((radius, mytype, '', minprice, maxprice))
        typeq.join()


    def _nearby_search_one_type(self, myqueue):
        while True:
            radius, mytype, keyword, minprice, maxprice = myqueue.get()
            urldir = '/place/nearbysearch/json?'
            urldir += apikey
            urldir += '&location=' + str(self.location['lat']) + ',' + str(self.location['lng'])
            urldir += '&radius=' + str(radius)
            if keyword != '':
                urldir += '&keyword=' + urllib.parse.quote(keyword)
            if mytype != '':
                urldir += '&type=' + mytype
            urldir += '&fields=place_id'
            data = dataFromURL(url + urldir)
            if 'error_message' in data:
                raise Exception('Error: nearby_search: error message: ' + data['error_message'])
            if data['results'] is None:
                myqueue.task_done()
            for aresult in data['results']:
                if aresult['place_id'] not in self.googleidlist:
                    self.googleidlist.append(aresult['place_id'])
            if 'next_page_token' in data:
                sleep(5)
                self.nearby_search_nextpage(data['next_page_token'])
            myqueue.task_done()

        
    def nearby_search_one_type(self, radius, mytype, keyword='', minprice=0, maxprice=4):
        '''
        Finds a list of places nearby to the given location in the set radius.
        returns an array of google place ids
        '''
        #mylocation = street_address_to_lat_lng(self.location)
        urldir = '/place/nearbysearch/json?'
        urldir += apikey
        urldir += '&location=' + str(self.location['lat']) + ',' + str(self.location['lng'])
        urldir += '&radius=' + str(radius)
        if keyword != '':
            urldir += '&keyword=' + urllib.parse.quote(keyword)
        if mytype != '':
            urldir += '&type=' + mytype
        urldir += '&fields=place_id'
        data = dataFromURL(url + urldir)
        if 'error_message' in data:
            raise Exception('Error: nearby_search: error message: ' + data['error_message'])
        if data['results'] is None:
            return
        for aresult in data['results']:
            if aresult['place_id'] not in self.googleidlist:
                self.googleidlist.append(aresult['place_id'])
        if 'next_page_token' in data:
            sleep(5)
            self.nearby_search_nextpage(data['next_page_token'])

        
    def nearby_search_nextpage(self, token, sleeptime=3):
        '''
        Gets a list of restaraunt from a next page token
        input: string containing token
        output: list of restaraunt dictionaries
        '''
        urldir = "&".join( ('/place/nearbysearch/json?pagetoken=' + token, apikey,))
        data = dataFromURL(url + urldir)
        if 'error_message' in data:
            raise Exception('_nearby_search_nextpage: error_message: ' + data['error_message'])
        for aresult in data['results']:
            if aresult['place_id'] not in self.googleidlist:
                self.googleidlist.append(aresult['place_id'])
        if 'next_page_token' in data:
            self.nearby_search_nextpage(data['next_page_token'])
        
    def get_googleidlist(self):
        if self.googleidlist is None:
            return []
        return self.googleidlist

    def getplaceidlist(self, jobnumber=0):
        if len(self.placeidlist) > 0:
            return self.placeidlist
        for i in range(5):
            worker = threading.Thread(target=self._get_place_id_list, args=(q,))
            worker.setDaemon(False)
            worker.start()
        for googleid in self.googleidlist:
            q.put((googleid, jobnumber))
        q.join()
        myjob = JobList.query.filter(JobList.id == jobnumber).first()
        myjob.googlecomplete = True
        db_session.commit()
        return self.placeidlist

    def _get_place_id_list(self, myqueue):
        while True:
            googleid, jobnumber = myqueue.get()
            mygoogleplace = googleplace(googleid)
            mygoogleplace.get_googleplaceid()
            self.placeidlist.append(mygoogleplace.get_placeid())
            mygoogleplace.set_categories()
            mygoogleplace.openinghours_to_db()
            mygoogleplace.set_jobnumber(jobnumber)
            myqueue.task_done()


class googleplace:
    placeid = 0
    googleplaceid = 0
    myjson = dict()
    googleid = ""

    jobnumber = int()
    location = dict()
    googleplacerecord = GooglePlace()
    placerecord = Places()
    refresh = False

    def __init__(self, googleid, refresh=False):
        self.googleid = googleid
        self.refresh = refresh
        self.get_place_details()
        

    def get_place_details(self):
        self.googleplacerecord = GooglePlace.query.filter(GooglePlace.googleplace_id == self.googleid).first()
        if (self.googleplacerecord is not None) and (not self.refresh):
            self.get_placeid()
            self.get_googleplaceid()
        else:
            fields = ['place_id', 'rating', 'address_component', 'business_status', 'geometry', 'name', 'type', 'vicinity', 'url', 'website','international_phone_number', 'opening_hours', 'price_level', 'user_ratings_total', 'plus_code']
            urldir = '/place/details/json?'
            urldir = urldir + apikey
            urldir = urldir + '&place_id='
            urldir = urldir + str(self.googleid)
            urldir = urldir + '&fields='
            urldir = urldir + ','.join(fields)
            fullurl = url + urldir
            self.myjson = dataFromURL(fullurl)

    def get_googleplaceid(self):
        if (self.googleplaceid == 0) or (self.googleplaceid is None):
            self.googleplaceid = self.set_googleplaceid()
        return self.googleplaceid
    
    def set_googleplaceid(self):
        self.googleplacerecord = GooglePlace.query.filter(GooglePlace.googleplace_id == self.googleid).first()
        if self.googleplacerecord is not None:
            self.googleplaceid = self.googleplacerecord.id
            if not self.refresh:
                return self.googleplacerecord.id
        if 'result' not in self.myjson:
            return 0
        aresult = self.myjson['result']
        if 'business_status' in aresult:
            business_status = business_status_dict[aresult['business_status']]
        else:
            business_status = 1
        viewportnelat = aresult['geometry']['viewport']['northeast']['lat']
        viewportnelng = aresult['geometry']['viewport']['northeast']['lng']
        viewportswlat = aresult['geometry']['viewport']['southwest']['lat']
        viewportswlng = aresult['geometry']['viewport']['southwest']['lng']
        lat = aresult['geometry']['location']['lat']
        lng = aresult['geometry']['location']['lng']
        if 'plus_code' in aresult:
            pluscode = aresult['plus_code']['global_code']
        else:
            pluscode = openlocationcode.encode(lat, lng)
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
            website=website,
            pluscode=pluscode)
        db_session.add(self.googleplacerecord)
        db_session.commit()
        return self.googleplacerecord.id

    def get_placeid(self):
        if (self.placeid is not None) and (self.placeid > 0):
            return self.placeid
        if (self.googleplacerecord is None) or (self.googleplacerecord.placeid is None):
            self.set_placeid()
        if self.googleplacerecord is not None:
            self.placeid = self.googleplacerecord.placeid
            return self.placeid
        else:
            return 0

    def set_placeid(self, placeid=0):
        self.placerecord = Places.query.filter(Places.id == placeid).first()
        if self.placerecord is None:
            if self.myjson is None:
                self.get_place_details()
            if 'result' not in self.myjson: 
                return
            aresult = self.myjson['result']
            name = aresult['name']
            address_components = aresult['address_components']
            street1 = _make_street1(address_components)
            suburb = _get_address_component(address_components, 'locality')
            restaurantstate = _get_address_component(address_components, 'administrative_area_level_1')
            postcode = _get_address_component(address_components, 'postal_code')
            vicinity = street1 + ', ' + suburb + ' ' + restaurantstate + ', ' + postcode
            phonenumber = '+61000000000'
            pluscode = self.get_pluscode()
            if 'international_phone_number' in aresult:
                phonenumber = aresult['international_phone_number'].replace(' ', '')
            self.placerecord = Places(placename=name, 
                googleplaceid=self.get_googleplaceid(), 
                street1=street1, suburb=suburb, 
                vicinity=vicinity, 
                postcode=postcode, 
                placestate=restaurantstate, 
                phonenumber=phonenumber,
                pluscode=pluscode)
            db_session.add(self.placerecord)
            db_session.commit()
            self.placeid = self.placerecord.id            
        else:
            self.placeid = placeid
        self.placerecord.googleplaceid = self.get_googleplaceid()
        if self.googleplaceid > 0:
            self.googleplacerecord.placeid = self.placeid
            db_session.commit()


    def set_categories(self):
        if self.myjson is None:
            self.get_place_details()
        if (self.myjson is not None) and ('result' in self.myjson):
            types = self.myjson['result']['types']
            for mytype in types:
                add_type_to_place(self.get_placeid(), mytype)

    def openinghours_to_db(self):
        if (self.get_placeid() == 0) or ('result' not in self.myjson) :
            return
        if 'opening_hours' not in self.myjson['result']:
            return
        open_hours_ob = self.myjson['result']['opening_hours']
        oh = OpeningHours.query.filter(OpeningHours.placeid == self.get_placeid()).first()
        if oh is None:
            oh = OpeningHours(self.get_placeid())
        for period in open_hours_ob['periods']:
            #open24 hours
            if (period['open']['day'] == 0) and (period['open']['time'] == '0000') and (period.get('close') is None):
                oh = OpeningHours(self.get_placeid(), '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359')
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
        if self.get_placeid() == 0:
            return
        db_session.add(JobResults(placeid=self.get_placeid(), jobid=jobnumber))
        db_session.commit()

    def get_location(self):
        location = dict(lat = self.googleplacerecord.lat,
            lng = self.googleplacerecord.lng)
        return location
    
    def get_pluscode(self):
        mylocation = self.get_location()
        return openlocationcode.encode(mylocation['lat'], mylocation['lng'])
        
    


