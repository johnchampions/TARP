from queue import Queue
from . import gs
from . import zs
from .db import db_session
from .models import YelpPlace, Places, JobResults, OpeningHours, JobList
from .tar_helper import add_type_to_place, getapikey
import urllib.request, urllib.parse, urllib.error
from json import loads
from time import sleep
import random
from openlocationcode import openlocationcode
import threading

url = "https://api.yelp.com/v3/businesses/search?"
apikey = getapikey('yelpapikey')

def dataFromURL(fullURL, url_params):
    """Grabs a file off the internet.
    input: full URL of the file
    output: a string containing the server response, usually a file
    """
    print(fullURL)
    params = urllib.parse.urlencode(url_params)
    request = urllib.request.Request(fullURL + params)
    request.add_header("Authorization", apikey)
    errorcount = 0
    max_error_count = 5
    while errorcount < max_error_count:
        try:
            response = urllib.request.urlopen(request)
            jsonData = loads(response.read())
            if 'error' in jsonData.keys():
                errorcount = errorcount + 1
            else:
                return jsonData 

        except urllib.error.URLError as e:
            errorcount = errorcount + 1
            sleep(random.random() * 10)
    return ''
        


class yelpsearch:
    yelpidlist = []
    placeidlist = []
    q = Queue()

    def __init__(self,location, radius, categories, minprice=1, maxprice=4, keyword=''):
        self.nearby_places(location, radius, categories, minprice, maxprice, keyword)
        
    def get_yelpidlist(self):
        if self.yelpidlist is None:
            return []
        return self.yelpidlist


    def nearby_places(self, location, radius, categories, minprice=1, maxprice=4, keyword=''):
        params = dict()
        params['radius'] = str(radius)
        params['latitude'] = str(location['lat'])
        params['longitude'] = str(location['lng'])
        params['limit'] = '50'
        params['offset'] = '0'
        if len(categories) > 0:
            params['categories'] = ','.join(categories)
        if keyword != '':
            params['term'] = keyword
        data = dataFromURL(url, params)
        if 'error_message' in data:
            raise Exception('YelpScrape2.nearbysearch: ' + data['error_message'])
        self.yelpidlist.extend(self.get_list_of_locations(data))
        if int(data['total']) > int(params['limit']):
            self.yelpidlist.extend(self.nearby_search_next_page(params))

    def get_list_of_locations(self, data):
        output = []
        if 'businesses' in data:
            for business in data['businesses']:
                output.append(business['id'])
        return output
    
    def nearby_search_next_page(self, params):
        output = []
        limit = int(params['limit'])
        offset = int(params['offset']) + limit
        params['offset'] = str(offset)
        if offset + limit > 1000:
            limit = 1000 - offset
        params['limit'] = str(limit)
        data = dataFromURL(url, params)
        if data == '':
            return output
        if 'error_message' in data:
            raise Exception('YelpScrape2.nearbysearch: ' + data['error_message'])
        output.extend(self.get_list_of_locations(data))
        if (data['total'] > offset + limit)  and (1000 > offset + limit):
            output.extend(self.nearby_search_next_page(params))
        return output

    def get_placeidlist(self, jobnumber=0):
        if len(self.placeidlist) > 0:
            return self.placeidlist
        if self.yelpidlist is None:
            return []
        for i in range(5):
            worker = threading.Thread(target=self._get_single_place, args=(self.q,))
            worker.setDaemon(True)
            worker.start()
        for yelpid in self.yelpidlist:
            self.q.put((yelpid, jobnumber))
        self.q.join()
        myjob = JobList.query.filter(JobList.id == jobnumber).first()
        myjob.yelpcomplete = True
        db_session.commit()
        return self.placeidlist

    def _get_single_place(self, myqueue):
        while True:
            yelpid, jobnumber = myqueue.get()
            myyelpplace = yelpplace(yelpid)
            myyelpplace.get_yelpplaceid()
            self.placeidlist.append(myyelpplace.get_placeid())
            myyelpplace.set_categories()
            myyelpplace.openinghours_to_db()
            myyelpplace.set_jobnumber(jobnumber)
            mygooglesearch = gs.googlesearch(myyelpplace.get_location(),100,[], myyelpplace.get_placename())
            if len(mygooglesearch.get_googleidlist()) != 0:
                mygoogleplace = gs.googleplace(mygooglesearch.get_googleidlist()[0])
                googleplaceid = mygoogleplace.get_googleplaceid()
                if googleplaceid > 0:
                    mygoogleplace.set_placeid(myyelpplace.get_placeid())
                    mygoogleplace.set_categories()
            myqueue.task_done()    

    def get_single_place(self, yelpid, jobnumber):
        myyelpplace = yelpplace(yelpid)
        myyelpplace.get_yelpplaceid()
        self.placeidlist.append(myyelpplace.get_placeid())
        myyelpplace.set_categories()
        myyelpplace.openinghours_to_db()
        myyelpplace.set_jobnumber(jobnumber)
        mygooglesearch = gs.googlesearch(myyelpplace.get_location(),100,[], myyelpplace.get_placename())
        if len(mygooglesearch.get_googleidlist()) != 0:
            mygoogleplace = gs.googleplace(mygooglesearch.get_googleidlist()[0])
            googleplaceid = mygoogleplace.get_googleplaceid()
            if googleplaceid > 0:
                mygoogleplace.set_placeid(myyelpplace.get_placeid())
                mygoogleplace.set_categories()

class yelpplace:
    placeid = 0
    yelpplaceid = 0
    myjson = dict()
    yelpid = ""
    jobnumber = int()
    location = dict()
    yelpplacerecord = YelpPlace()
    placerecord = Places()

    def __init__(self, yelpid):
        self.yelpid = yelpid
        self.myjson = self.get_place_details()

    def get_yelpplaceid(self):
        if self.yelpplaceid == 0:
            self.set_yelpplaceid()
        return self.yelpplaceid

    def set_yelpplaceid(self):
        self.yelpplacerecord = YelpPlace.query.filter(YelpPlace.yelpplace_id == self.yelpid).first()
        if self.yelpplacerecord is not None:
            self.yelpplaceid = self.yelpplacerecord.id
            return self.yelpplacerecord.id
        self.get_place_details()
        business_status = 1
        if self.myjson['is_closed']:
            business_status = 0
        lat = self.myjson['coordinates']['latitude']
        lng = self.myjson['coordinates']['longitude']
        if 'price' in self.myjson:
            price_level = len(self.myjson['price'])
        else:
            price_level = 0
        rating = self.myjson['rating']
        user_ratings_total = self.myjson['review_count']
        placeurl = self.myjson['url']

        self.yelpplacerecord = YelpPlace(business_status=business_status, 
            lat=lat, 
            lng=lng,
            price_level=price_level, 
            rating=rating, 
            user_ratings_total=user_ratings_total,
            yelpplace_id=self.yelpid, 
            website=placeurl)
        db_session.add(self.yelpplacerecord)
        db_session.commit()
        self.yelpplaceid = self.yelpplacerecord.id

    def get_placeid(self):
        if self.placeid > 0:
            return self.placeid
        if self.yelpplacerecord.placeid is None:
            self.set_placeid()
        self.placeid = self.yelpplacerecord.placeid
        return self.placeid
        
        
    def set_placeid(self, placeid=0):
        self.placerecord = Places.query.filter(Places.id == placeid).first()
        if self.placerecord is None:
            placename = self.myjson['name']
            vicinity = ', '.join(self.myjson['location']['display_address'])
            street1 = self.myjson['location']['address1']
            street2 = self.myjson['location']['address2']
            suburb = self.myjson['location']['city']
            postcode = self.myjson['location']['zip_code']
            placestate = self.myjson['location']['state']
            phone = '+61000000000'
            phone = self.myjson['phone']
            pluscode = self.get_pluscode()
            self.placerecord = Places(placename, yelpplaceid=self.get_yelpplaceid(), vicinity=vicinity, street1=street1, street2=street2,
                suburb=suburb, postcode=postcode, placestate=placestate, phonenumber=phone, pluscode=pluscode)
            db_session.add(self.placerecord)
            db_session.commit()
            self.placeid = self.placerecord.id    
        else:
            self.placeid = placeid
        self.placerecord.yelpplaceid = self.get_yelpplaceid()
        self.yelpplacerecord.placeid = self.placeid
        db_session.commit()

    def set_categories(self):
        if self.myjson is None:
            self.get_place_details()
        if self.myjson is not None:
            for category in self.myjson['categories']:
                add_type_to_place(self.get_placeid(), category['title'])


    def get_place_details(self):
        self.yelpplacerecord = YelpPlace.query.filter(YelpPlace.yelpplace_id == self.yelpid).first()
        if self.yelpplacerecord is not None:
            self.get_placeid()
            self.get_yelpplaceid()
        else:
            myurl = 'https://api.yelp.com/v3/businesses/'
            params = dict()
            urldir = myurl + self.yelpid
            data = dataFromURL(urldir, params)
            return data
        

    def openinghours_to_db(self):
        if self.myjson is None:
            return
        if (self.get_placeid() == 0) or ('hours' not in self.myjson):
            return
        open_hours_ob = self.myjson['hours']
        if OpeningHours.query.filter(OpeningHours.placeid == self.get_placeid()).first() is None:
            oh = OpeningHours(self.get_placeid())
            for period in open_hours_ob[0]['open']:
                if period['day'] == 0:
                    oh.sundayopen = period['start']
                    oh.sundayclose = period['end']
                if period['day'] == 1:
                    oh.mondayopen = period['start']
                    oh.mondayclose = period['end']
                if period['day'] == 2:
                    oh.tuesdayopen = period['start']
                    oh.tuesdayclose = period['end']
                if period['day'] == 3:
                    oh.wednesdayopen = period['start']
                    oh.wednesdayclose = period['end']
                if period['day'] == 4:
                    oh.thursdayopen = period['start']
                    oh.thursdayclose = period['end']
                if period['day'] == 5:
                    oh.fridayopen = period['start']
                    oh.fridayclose = period['end']
                if period['day'] == 6:
                    oh.saturdayopen = period['start']
                    oh.saturdayclose = period['end']
            db_session.add(oh)
            db_session.commit()

    def set_jobnumber(self, jobnumber):
        db_session.add(JobResults(placeid=self.get_placeid(), jobid=jobnumber))
        db_session.commit()

    def get_location(self):
        location = dict(lat = self.yelpplacerecord.lat,
            lng = self.yelpplacerecord.lng)
        return location
    
    def get_placename(self):
        self.placerecord = Places.query.filter(Places.id == self.placeid).first()
        return self.placerecord.placename

    def get_pluscode(self):
        mylocation = self.get_location()
        return openlocationcode.encode(mylocation['lat'], mylocation['lng'])