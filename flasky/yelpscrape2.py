from sqlalchemy.sql.expression import false
from flasky.models import KeyWords, OpeningHours, Places, Reviews, YelpPlace, JobResults
import urllib.request
import urllib.parse
import urllib.error
import json
from flasky.db2 import db_session
from flasky.zomatoscrape2 import place_to_db
from . import tar_helper as helper
from . import googlescrape2

apikey = helper.getapikey('yelpapikey')
url = "https://api.yelp.com/v3/businesses/search?"

def dataFromURL(fullURL, url_params):
    """Grabs a file off the internet.
    input: full URL of the file
    output: a string containing the server response, usually a file
    """
    params = urllib.parse.urlencode(url_params)
    request = urllib.request.Request(fullURL + params)
    request.add_header("Authorization", apikey)
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        raise Exception("Unexpected Error: " + fullURL + " : " + e.reason)
    jsonData = json.loads(response.read())
    return jsonData

def get_list_of_locations(data):
    '''
    Takes in json data from a yelp search
    Returns list of unique identifiers for each business in the searc
    '''
    output = []
    for business in data['businesses']:
        output.append(business['id'])
    return output

def nearby_search_next_page(params):
    '''
    Takes in dictionary with next page toketn,
    returns list of unique business idetifiers in the remaining pages
    '''
    output = []
    limit = int(params['limit'])
    offset = int(params['offset']) + limit
    params['offset'] = str(offset)
    if offset + limit > 1000:
        limit = 1000 - offset
    params['limit'] = str(limit)
    try:
        data = dataFromURL(url, params)
    except:
        data = dict(error_message='Error 500 Yelp server error.')
    if 'error_message' in data:
        raise Exception('YelpScrape2.nearbysearch: ' + data['error_message'])
    output.extend(get_list_of_locations(data))
    if (data['total'] > offset + limit)  and (1000 > offset + limit):
        try:
            output.extend(nearby_search_next_page(params))
        except:
            pass
    return output


def nearby_places(location, radius, categories, minprice=1, maxprice=4, keyword=''):
    '''
    Takes location dict radius and categories
    returns list of unique business ids
    '''
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
    businesslist = []
    if 'error_message' in data:
        raise Exception('YelpScrape2.nearbysearch: ' +
                        data['error_message'])
    businesslist.extend(get_list_of_locations(data))
    if int(data['total']) > int(params['limit']):
        businesslist.extend(nearby_search_next_page(params))
    return businesslist


def yelp_place_to_db(data, refresh=false):
    yelpplace_id = data['id']
    yelpplace = YelpPlace.query.filter(YelpPlace.yelpplace_id == yelpplace_id).first()
    if yelpplace is not None:
        return yelpplace.id
    
    business_status = 1
    if data['is_closed']:
        business_status = 0
    lat = data['coordinates']['latitude']
    lng = data['coordinates']['longitude']
    if 'price' in data:
        price_level = len(data['price'])
    else:
        price_level = 0
    rating = data['rating']
    user_ratings_total = data['review_count']
    placeurl = data['url']

    yelpplace = YelpPlace(business_status=business_status, 
        lat=lat, 
        lng=lng,
        price_level=price_level, 
        rating=rating, 
        user_ratings_total=user_ratings_total,
        yelpplace_id=yelpplace_id, 
        website=placeurl)
    db_session.add(yelpplace)
    db_session.commit()
    return yelpplace.id


def place_to_db(myjson, yelpplaceid, place_id=0):
    placename = myjson['name']
    vicinity = ', '.join(myjson['location']['display_address'])
    street1 = myjson['location']['address1']
    street2 = myjson['location']['address2']
    suburb = myjson['location']['city']
    postcode = myjson['location']['zip_code']
    placestate = myjson['location']['state']
    phone = '+61000000000'
    phone = myjson['phone']
    placerecord = Places.query.filter(Places.yelpplaceid == yelpplaceid).first()
    if placerecord is None:
        placerecord = Places(placename, yelpplaceid=yelpplaceid, vicinity=vicinity, street1=street1, street2=street2,
            suburb=suburb, postcode=postcode, placestate=placestate, phonenumber=phone)
        db_session.add(placerecord)
        db_session.commit()
    if (placerecord.id is None) and (place_id > 0):
        placerecord.id = 
    place_id = placerecord.id
    helper.add_keywords(get_categories(myjson), place_id)
    openinghours_to_db(myjson, place_id)
    return place_id


def get_categories(myjson):
    output = []
    for category in myjson['categories']:
        output.append(category['title'])
    return output


def openinghours_to_db( myjson, placeid):
    if 'hours' not in myjson:
        return
    open_hours_ob = myjson['hours']
    if OpeningHours.query.filter(OpeningHours.placeid == placeid).first() is None:
        oh = OpeningHours(placeid)
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


def get_place_details(place_ids, refresh=False, job_id=0):
    myurl = 'https://api.yelp.com/v3/businesses/'
    params = dict()
    output = []
    for place_id in place_ids:
        yelp_place = YelpPlace.query.filter(YelpPlace.yelpplace_id == place_id).first()
        if  yelp_place is not None:
            db_session.add(JobResults(placeid=yelp_place.placeid, jobid=job_id))
            db_session.commit()
            if refresh == False:
                continue
        urldir = myurl + place_id
        data = dataFromURL(urldir, params)
        yelpplaceid = yelp_place_to_db(data)
        output.append(yelpplaceid)
        db_session.commit()
        
    return output


def get_yelp_place_id(placeid):
    myplace = Places.query.filter(Places.id == placeid).first()
    if myplace is None:
        raise Exception("Yeah nah.  place does not exist " + str(placeid))
    if myplace.yelpplaceid is not None:
        return myplace.yelpplaceid
    mylist = nearby_places(helper.get_location_from_placeid(placeid), 100, (), keyword=myplace.placename)
    my_yelp_ids = get_place_details(mylist)
    if len(my_yelp_ids) > 0:
        return my_yelp_ids[0]
    return 0



class ys2:

    def __init__(self, apikey):
        self.apikey = apikey
        self.url = "https://api.yelp.com/v3/businesses/search?"
        self.db_session = db_session
        

    def dataFromURL(self, fullURL, url_params):
        """Grabs a file off the internet.
        input: full URL of the file
        output: a string containing the server response, usually a file
        """
    
        params = urllib.parse.urlencode(url_params)
        request = urllib.request.Request(fullURL + params)
        request.add_header("Authorization", self.apikey)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            raise Exception("Unexpected Error: " + fullURL + " : " + e.reason)
        jsonData = json.loads(response.read())
        return jsonData

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
        data = self.dataFromURL(self.url, params)
        businesslist = []
        if 'error_message' in data:
            raise Exception('YelpScrape2.nearbysearch: ' + data['error_message'])
        businesslist.extend(self.get_list_of_locations(data))
        if int(data['total']) > int(params['limit']):
            businesslist.extend(self.nearby_search_next_page(params))
        return businesslist
        
    
    def nearby_search_next_page(self, params):
        output = []
        limit = int(params['limit'])
        offset = int(params['offset']) + limit
        params['offset'] = str(offset)
        if offset + limit > 1000:
            limit = 1000 - offset
        params['limit'] = str(limit)
        data = self.dataFromURL(self.url, params)
        
        if 'error_message' in data:
            raise Exception('YelpScrape2.nearbysearch: ' + data['error_message'])
        output.extend(self.get_list_of_locations(data))
        if (data['total'] > offset + limit)  and (1000 > offset + limit):
            output.extend(self.nearby_search_next_page(params))
        return output
        

    def get_list_of_locations(self, data):
        output = []
        for business in data['businesses']:
            output.append(business['id'])
        return output

    def get_place_details(self, place_ids, refresh=False, job_id=0):
        myurl = 'https://api.yelp.com/v3/businesses/'
        params = dict()
        for place_id in place_ids:
            go_nogo = YelpPlace.query.filter(YelpPlace.yelpplace_id == place_id).first()
            if  go_nogo is not None:
                db_session.add(JobResults(placeid=go_nogo.placeid, jobid=job_id))
                db_session.commit()
                if refresh == False:
                    continue
            urldir = myurl + place_id
            data = self.dataFromURL(urldir, params)
            placeid = self.place_to_db(data)
            db_session.add(JobResults(placeid=placeid, jobid=job_id))
            db_session.commit()

    def place_to_db(self, data):
        categories = self.get_categories(data['categories'])
        placename = data['name']
        business_status = 1
        if data['is_closed']:
            business_status = 0
        lat = data['coordinates']['latitude']
        lng = data['coordinates']['longitude']
        if 'price' in data:
            price_level = len(data['price'])
        else:
            price_level = 0
        rating = data['rating']
        user_ratings_total = data['review_count']
        yelpplace_id = data['id']
        vicinity = ', '.join(data['location']['display_address'])
        street1 = data['location']['address1']
        street2 = data['location']['address2']
        suburb = data['location']['city']
        postcode = data['location']['zip_code']
        placestate = data['location']['state']
        phone = '+61000000000'
        phone = data['phone']
        placeurl = data['url']
        
        yelpplace = YelpPlace.query.filter(YelpPlace.yelpplace_id == yelpplace_id).first()
        if yelpplace is None:
            yelpplace = YelpPlace(business_status=business_status, lat=lat, lng=lng,
                price_level=price_level, rating=rating, user_ratings_total=user_ratings_total,
                yelpplace_id=yelpplace_id, website=placeurl)
            self.db_session.add(yelpplace)
            self.db_session.commit()
        
        placerecord = Places.query.filter((Places.placename == placename) and (Places.phonenumber == phone) and (Places.postcode == postcode)).first()
        if placerecord is None:
            placerecord = Places(placename, yelpplaceid=yelpplace.id, vicinity=vicinity, street1=street1, street2=street2,
                suburb=suburb, postcode=postcode, placestate=placestate, phonenumber=phone)
            self.db_session.add(placerecord)
            self.db_session.commit()
        yelpplace.placeid = placerecord.id
        self.db_session.commit()

        blacklist = helper.get_blacklist()
        for mytype in categories:
            if mytype in blacklist:
                continue
            my_type_record = KeyWords.query.filter(KeyWords.placeid == placerecord.id, KeyWords.placetype == mytype).first()
            if my_type_record is None:
                keyword = KeyWords(placerecord.id, mytype)
                self.db_session.add(keyword)
        self.db_session.commit()
        self._get_reviews(placerecord.id)
        if 'hours' in data:
            self._openinghours_to_db(data['hours'], placerecord.id)
        return placerecord.id


    def _get_reviews(self, placeid, locale='en_AU'):
        yelprecord = YelpPlace.query.filter(YelpPlace.placeid == placeid).first()
        myurl = 'https://api.yelp.com/v3/businesses/' + yelprecord.yelpplace_id + '/reviews'
        params = dict()
        params['locale'] = locale
        try :
            data = self.dataFromURL(myurl, params)
        except:
            data = {'reviews' : []}
        for review in data['reviews']:
            reviewrecord = Reviews(placeid, review['rating'], review['text'], 'yelp')
            self.db_session.add(reviewrecord)
        self.db_session.commit()
        

     
    def _openinghours_to_db(self, open_hours_ob, placeid):
        oh = OpeningHours.query.filter(OpeningHours.placeid == placeid).first()
        if oh is None:
            oh = OpeningHours(placeid)
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
        self.db_session.add(oh)
        self.db_session.commit()
        

    def get_categories(self, category_dicts):
        output = []
        for category in category_dicts:
            output.append(category['title'])
        return output
        
