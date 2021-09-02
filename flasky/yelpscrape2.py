from flasky.models import KeyWords, OpeningHours, Places, Reviews, YelpPlace, JobResults
import urllib.request
import urllib.parse
import json
from flasky.db2 import db_session

def mash_yelp_places(new_place, old_place):
    if new_place.business_status is None:
        new_place.business_status = old_place.business_status
    if new_place.lat is None:
        new_place.lat = old_place.lat
    if new_place.lng is None:
        new_place.lng = old_place.lng
    if new_place.price_level is None:
        new_place.price_level = old_place.price_level
    if new_place.rating is None:
        new_place.rating = old_place.rating
    if new_place.user_ratings_total is None:
        new_place.user_ratings_total = old_place.user_ratings_total
    if new_place.website is None:
        new_place.website = old_place.website
    return new_place

def mash_places(new_place, old_place):
    if new_place.placename is None:
        new_place.placename = old_place.placename
    if new_place.street1 is None:
        new_place.street1 = old_place.street1
    if new_place.street2 is None:
        new_place.street2 = old_place.street1
    if new_place.suburb is None:
        new_place.suburb = old_place.suburb
    if new_place.vicinity is None:
        new_place.vicinity = old_place.vicinity
    if new_place.postcode is None:
        new_place.postcode = old_place.postcode
    if new_place.placestate is None:
        new_place.placestate = old_place.placestate
    if new_place.phonenumber == '+61000000000':
        new_place.phonenumber = old_place.phonenumber
    return new_place

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
            if YelpPlace.query.filter(YelpPlace.yelpplace_id == place_id).first() is not None:
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

        for mytype in categories:
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
        