from flasky.models import GooglePlace, KeyWords, OpeningHours, Places, Reviews
import flasky.tar_helper as th
import urllib.request
import urllib.parse
import json
from datetime import datetime
import time
from flasky.db2 import db_session

'''
What we wanna do?

This version of the scraper will grab all the fields that the user wishes
to collect from the Google Places API.

It will report back with a list of places, and set up a background tasks
to grab the details and stick them in the database.

Once all are collected, they will generate the HTMLreport/xls/cvs report.

I think...

'''

def mash_google_places(new_place, old_place):
    if new_place.business_status is None:
        new_place.business_status = old_place.business_status
    if new_place.viewportnelat is None:
        new_place.viewportnelat = old_place.viewportnelat
    if new_place.viewportnelng is None:
        new_place.viewportnelng = old_place.viewportnelng
    if new_place.viewportswlat is None:
        new_place.viewportswlat = old_place.viewportswlat
    if new_place.viewportswlng is None:
        new_place.viewportswlng = old_place.viewportswlng
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
    if new_place.placeurl is None:
        new_place.placeurl = old_place.placeurl
    if new_place.website is None:
        new_place.website = old_place.website
    return new_place

def mash_places(new_place, old_place):
    if new_place.placename is None:
        new_place.placename = old_place.placename
    if new_place.street1 is None:
        new_place.street1 = old_place.street1
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

class gs2:

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


    def __init__(self, apikey):
        self.apikey = apikey
        self.url = 'https://maps.googleapis.com/maps/api'
        self.db_session = db_session

    def street_address_to_lat_lng(self, street_address):
        '''
        Converts a street address to a latitude/longitude dictionary
        input: string containing street address.
        output: dictionary of lat, lng
        '''

        urldir = "/place/findplacefromtext/json?&inputtype=textquery&fields=geometry&" + self.apikey
        latlongdict = {
            "lat": "",
            "lng": ""
        }

        urldir = urldir + "&input=" + urllib.parse.quote(street_address)
        data = th.dataFromURL(self.url + urldir)
        if len(data['candidates']) == 0:
            raise Exception(
                "Error: streetAddressToLatLong: Couldn't find Address. " + urldir)
        if "error_message" in data:
            raise Exception(
                "Error: streetAddressToLatLong: error_message: " + data['error_message'])
        latlongdict['lat'] = data['candidates'][0]['geometry']['location']['lat']
        latlongdict['lng'] = data['candidates'][0]['geometry']['location']['lng']
        return latlongdict

    def find_place(self, input, is_phone_number=False):
        '''
        Finds a place based on name or phone nymber.
        Returns array of google place IDs.
        '''

        urldir = '/place/findplacefromtext/json?'
        if is_phone_number:
            urldir += '&inputtype=phonenumber'
        else:
            urldir += '&inputtype=textquery'
        urldir += '&fields=place_id&' + self.apikey
        urldir += '&input=' + urllib.parse.quote(input)
        data = th.dataFromURL(self.url + urldir)
        if len(data['candidates']) == 0:
            raise Exception(
                "Error: find_place: couldn't find an entry for your input." + urldir)
        if 'error_message' in data:
            raise Exception(
                'Error: find_place: error message: ' + data['error_message'])
        output = []
        for aresult in data['candidates']:
            output.extend( self.get_one_dimensional_list(aresult['place_id']))
        return output

    def find_place_from_text(self, input):
        '''
        Finds a place based on name or phone nymber.
        Returns array of google place IDs.
        '''

        urldir = '/place/textsearch/json?'
        urldir += '&fields=formatted_address' + self.apikey
        urldir += '&query=' + urllib.parse.quote(input)
        data = th.dataFromURL(self.url + urldir)
        if len(data['results']) == 0:
            raise Exception(
                "Error: find_place: couldn't find an entry for your input." + urldir)
        if 'error_message' in data:
            raise Exception(
                'Error: find_place: error message: ' + data['error_message'])
        output = []
        for result in data['results']:
            output.extend(self.get_one_dimensional_list(result['place_id']))
        return output
        

    def get_one_dimensional_list(self,mylist):
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
                    output.extend(self.get_one_dimensional_list(item))
                else:
                    output.append(item)
        return output

    def nearby_search_one_type(self, location, radius, mytype, keyword='', minprice=0, maxprice=4):
        '''
        Finds a list of places nearby to the given location in the set radius.
        returns an array of google place ids
        '''
        mylocation = self.street_address_to_lat_lng(location)
        urldir = '/place/nearbysearch/json?'
        urldir += self.apikey
        urldir += '&location=' + str(mylocation['lat']) + ',' + str(mylocation['lng'])
        urldir += '&radius=' + radius
        if keyword != '':
            urldir += '&keyword=' + urllib.parse.quote(keyword)
        if mytype != '':
            urldir += '&type=' + mytype
        urldir += '&fields=place_id'
        data = th.dataFromURL(self.url + urldir)
        if 'error_message' in data:
            raise Exception(
                'Error: nearby_search: error message: ' + data['error_message'])
        output = []
        for aresult in data['results']:
            output.extend(self.get_one_dimensional_list(aresult['place_id']))
        if 'next_page_token' in data:
            output.extend(self._nearby_search_nextpage(data['next_page_token']))
        return output

    def _nearby_search_nextpage(self, token):
        '''
        Gets a list of restaraunt from a next page token
        input: string containing token
        output: list of restaraunt dictionaries
        '''
        urldir = "&".join( ('/place/nearbysearch/json?pagetoken=' + token, self.apikey,))
        time.sleep(3)
        data = th.dataFromURL(self.url + urldir)
        if 'error_message' in data:
            raise Exception(
                '_nearby_search_nextpage: error_message: ' + data['error_message'])
        output = []
        for aresult in data['results']:
            output.extend(self.get_one_dimensional_list(aresult['place_id']))
        return output

    def _remove_repeats_across_lists(firstlist, secondlist):
        '''
        Combines lists into one giant list and amalgamates scores and such
        '''
        if len(firstlist) == 0:
            return secondlist
        if len(secondlist) == 0:
            return firstlist
        returnlist = firstlist
        for myrecord in secondlist:
            if not myrecord in returnlist:
                returnlist.append(myrecord)
        return returnlist

    def nearby_places(self, location, radius, types, keyword='', language='en-AU', minprice=0, maxprice=4):
        '''
        Connector to
        '''
        output = []
        for type in types:
            output = self._remove_repeats_across_lists(
                output,
                self._nearby_search_one_type(location, radius, type, keyword=keyword, language=language, minprice=minprice, maxprice=maxprice))
        return output
   
    def get_place_details(self, place_ids, refresh=False, onlyaddress=False):
        fields = ['place_id', 'rating', 'address_component', 'business_status', 'geometry', 'name', 'type', 'vicinity', 'url', 'website','international_phone_number', 'opening_hours', 'price_level', 'user_ratings_total']
        if onlyaddress:
            fields = ['address_component']
        for place_id in place_ids:
            if (GooglePlace.query.filter(GooglePlace.googleplace_id == place_id).first() is not None):
                if refresh == False:
                    continue
            if type(place_id) is list:
                self.get_place_details(place_id)
            else:
                urldir = '/place/details/json?'
                urldir = urldir + self.apikey
                urldir = urldir + '&place_id='
                urldir = urldir + str(place_id)
                urldir = urldir + '&fields='
                urldir = urldir + ','.join(fields)
                ptang = self.url + urldir
                data = th.dataFromURL(ptang)
                self.place_to_db(data)
            if onlyaddress:
                return data['result']['address_components']

    def place_to_db(self, data):
        aresult = data['result']
        address_components = aresult['address_components']
        street1 = self._make_street1(address_components)
        suburb = self._get_address_component(address_components, 'locality')
        postcode = self._get_address_component(address_components, 'postal_code')
        restaurantstate = self._get_address_component(address_components, 'administrative_area_level_1')
        vicinity = street1 + ', ' + suburb + ' ' + restaurantstate + ', ' + postcode
        name = aresult['name']
        business_status = self.business_status_dict[aresult['business_status']]
        viewportnelat = aresult['geometry']['viewport']['northeast']['lat']
        viewportnelng = aresult['geometry']['viewport']['northeast']['lng']
        viewportswlat = aresult['geometry']['viewport']['southwest']['lat']
        viewportswlng = aresult['geometry']['viewport']['southwest']['lng']
        lat = aresult['geometry']['location']['lat']
        lng = aresult['geometry']['location']['lng']
        price_level = 0
        if 'price_level' in aresult:
            price_level = aresult['price_level']
        rating = -1
        if 'rating' in aresult:
            rating = aresult['rating']
        user_ratings_total = 0
        if 'user_ratings_total' in aresult:
            user_ratings_total = aresult['user_ratings_total']
               
        googleplace_id = aresult['place_id']
        phonenumber = '+61000000000'
        if 'international_phone_number' in aresult:
            phonenumber = aresult['international_phone_number'].replace(' ', '')
        placeurl = aresult['url']
        website = ''
        if 'website' in aresult:
            website = aresult['website']
        types = aresult['types']
        
        googleplace = GooglePlace.query.filter(GooglePlace.googleplace_id == googleplace_id).first()
        if googleplace is None:
            googleplace = GooglePlace(business_status=business_status, viewportnelat=viewportnelat,
            viewportnelng=viewportnelng, viewportswlat=viewportswlat, viewportswlng=viewportswlng,
            lat=lat, lng=lng, price_level=price_level, rating=rating, user_ratings_total=user_ratings_total,
            googleplace_id=googleplace_id, placeurl=placeurl, website=website)
            db_session.add(googleplace)
            db_session.commit()
        
        placerecord = Places.query.filter((Places.placename == name) and (Places.phonenumber == phonenumber) and (Places.postcode == postcode)).first()
        if placerecord is None:
            placerecord = Places(placename=name, googleplaceid=googleplace.id, street1=street1, suburb=suburb, 
                vicinity=vicinity, postcode=postcode, placestate=restaurantstate, phonenumber=phonenumber)
            db_session.add(placerecord)
            db_session.commit()
               
        googleplace.placeid = placerecord.id
        db_session.commit()
        
        for mytype in types:
            my_type_record = KeyWords.query.filter(KeyWords.placeid == placerecord.id, KeyWords.placetype == mytype).first()
            if my_type_record is None:
                keyword = KeyWords(placerecord.id, mytype)
                db_session.add(keyword)
        db_session.commit()
        
        if 'opening_hours' in aresult:
            self._openinghours_to_db(aresult['opening_hours'], placerecord.id)
        if 'reviews' in aresult:
            self._addgooglereviews(aresult['reviews'], placerecord.id)
    
    def _openinghours_to_db(self, open_hours_ob, placeid):
        oh = OpeningHours.query.filter(OpeningHours.placeid == placeid).first()
        if oh is None:
            oh = OpeningHours(placeid)
        for period in open_hours_ob['periods']:
            #open24 hours
            if (period['open']['day'] == 0) and (period['open']['time'] == '0000') and (period.get('close') is None):
                oh = OpeningHours(placeid, '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359', '0000', '2359')
                #if OpeningHours.query.filter(OpeningHours.placeid == placeid).first() is None:
                self.db_session.merge(oh)
                self.db_session.commit()
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
        self.db_session.merge(oh)
        self.db_session.commit()

    def _addgooglereviews (self,reviews_ob, placeid):
        for review in reviews_ob:
            review = Reviews(placeid, review['rating'], review['text'], 'google')
            self.db_session.add(review)
        self.db_session.commit()
    
    def _make_street1(self, address_object):
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

    def _get_address_component( self, address_object, componentname):
        return_value = ''
        for entry in address_object:
            if componentname in entry['types']:
                return_value = entry['short_name']
        return return_value

    def make_timing_string(self, placeid):
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


    