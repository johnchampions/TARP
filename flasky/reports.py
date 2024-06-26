from math import atan2, floor, radians, sin, sqrt, cos
from flasky.models import CuisineList, GooglePlace, JobList, JobResults, KeyWords, OpeningHours, Places
import flasky.tar_helper as helper


def listofplaces_to_listofdict(listofplaces):
    output = []
    for place in listofplaces:
        if type(place) is list:
            output.extend(listofplaces_to_listofdict(place))
        else:
            mydict = {}
            placerecord = Places.query.filter(Places.id == place).first()
            if placerecord is None:
                continue
            mydict = {
                'placerow': {
                    'id': placerecord.id,
                    'placename' : placerecord.placename,
                    'vicinity' : placerecord.vicinity,
                    'phonenumber' : placerecord.phonenumber
                }
            }
            typesrecords = KeyWords.query.filter(KeyWords.placeid == place).all()
            foo = []
            for typesrecord in typesrecords:
                foo.append(typesrecord.placetype)
            mydict['types'] = ', '.join(foo)
            output.append(mydict)
    return output

def create_job_json(jobnumber):
    jobrecord = JobList.query.filter( JobList.id == jobnumber).first()
    return jobrecord.jobjson

def get_Keyword_type_list(keyname):
    mydict = { 'coffee' : CuisineList.coffee,
        'license' : CuisineList.license,
        'cuisine' : CuisineList.cuisine,
        'blacklist' : CuisineList.blacklist}
    
    cuisinerecords = CuisineList.query.filter(mydict[keyname] == True).all()
    output = []
    for record in cuisinerecords:
        output.append(record.placetype)
    return output

def distance_between_places(lat1, lng1, lat2, lng2):
    EarthRadius = 6373000.0
    rlat1 = radians(lat1)
    rlng1 = radians(lng1)
    rlat2 = radians(lat2)
    rlng2 = radians(lng2)
    dlon = rlng1 - rlng2
    dlat = rlat1 - rlat2
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    try:
        c = 2 * atan2(sqrt(a), sqrt(1-a))
    except:
        c = 0.0
    distance = EarthRadius * c
    return distance

def getKeywords(records):
    types_list = []
    for mytype in records:
        if mytype.placetype not in types_list:
            types_list.append(mytype.placetype)
    return ', '.join(types_list)


def is_open_for_meal(mealtime, mealtimeclose, placeid):
    mealtime = int(mealtime)
    mealtimeclose = int(mealtimeclose)
    openrecords = OpeningHours.query.filter(OpeningHours.placeid == placeid).first()
    if openrecords is None:
        return ''
    mydict = openrecords.__dict__
    mylistofdays = ('sunday','monday','tuesday','wednesday','thursday','friday','saturday')
    for myday in mylistofdays:
        if mydict[myday + 'open'] is None or mydict[myday + 'close'] is None:
            continue
        if mydict[myday + 'open'].isdigit():
            myopen = int(mydict[myday + 'open'])
        else:
            myopen = 0
        if mydict[myday + 'close'].isdigit():
            myclose = int(mydict[myday + 'close'])
        else: 
            myclose = 0
        if myclose < myopen:
            myclose = 2359
        if (myopen < mealtimeclose) and (myclose > mealtime):
            return 'Yes'
    return ''

def getlat(record=None):
    if record is not None:
        if record.lat is not None:
            return record.lat
    return 0.0

def getlng(record=None):
    if record is not None:
        if record.lng is not None:
            return record.lng
    return 0.0

def get_price_level(records):
    count = 0
    total = 0
    for record in records:
        if record is not None:
            if (record.price_level is not None) and (record.user_ratings_total is not None): 
                total = total + (record.user_ratings_total * record.price_level)
                count = count + record.user_ratings_total
    if count == 0:
        return 0
    else: 
        return total / count

def rounded_distance_between_places(lat1, lng1, lat2, lng2):
    distance = floor(distance_between_places(lat1, lng1, lat2, lng2))
    return distance

def is_keyword_in_config_keywords(configkeywords, keywordsrecords):
    for configkeyword in configkeywords:
        for keywordrecord in keywordsrecords:
            if keywordrecord.placetype == configkeyword:
                return 'Yes'
    return ''

def getKeywords(records):
    types_list = []
    for mytype in records:
        if mytype.placetype not in types_list:
            types_list.append(mytype.placetype)
    return ', '.join(types_list)


class uglyreport:
    def __init__(self, jobnumber):
        self.jobnumber = jobnumber
        self.myjob = JobList.query.filter(JobList.id == self.jobnumber).first()
        self.myplacesrecords = JobResults.query.filter(JobResults.jobid == self.jobnumber).all()
    
    def create_report(self):
        output = []
        for place in self.myplacesrecords:
            placerecord = Places.query.filter(Places.id == place.placeid).first()
            if placerecord is None:
                continue
            placerecord = placerecord.__dict__
            gprecord = GooglePlace.query.filter(GooglePlace.placeid == place.placeid).first()
            if gprecord is None:
                gprecord = GooglePlace()
            placerecord = {**gprecord.__dict__, **placerecord }
            ohrecord = OpeningHours.query.filter(OpeningHours.placeid == place.placeid).first()
            if ohrecord is None:
                ohrecord = OpeningHours()
            placerecord = {** ohrecord.__dict__, **placerecord}
            keywordsrecords = KeyWords.query.filter(KeyWords.placeid == place.placeid).all()
            placerecord['keywords'] = getKeywords(keywordsrecords)
            del placerecord['_sa_instance_state']
            output.append(placerecord)
        return output


class tarreport:
    mymeals = ('breakfast', 'lunch', 'dinner', 'supper',)
    def __init__(self, jobnumber):
        self.jobnumber = jobnumber
        self.meals = {}
        for meal in self.mymeals:
            try:
                self.meals[meal] = helper.getapikey(meal).replace(':', '')
                self.meals[meal + 'close'] = helper.getapikey(meal +'close').replace(':', '')
            except:
                raise Exception("It appears that mealtimes have not been configured")
        self.myjob = JobList.query.filter(JobList.id == self.jobnumber).first()
        self.myplacesrecords = JobResults.query.filter(JobResults.jobid == self.jobnumber).all()

    def create_tar_report(self):
        output = []
        
        coffeetypes = get_Keyword_type_list('coffee')
        licensedtypes = get_Keyword_type_list('license')

        for place in self.myplacesrecords:
            placerecord = Places.query.filter(Places.id == place.placeid).first()
            keywordsrecords = KeyWords.query.filter(
                KeyWords.placeid == place.placeid).all()
            gprecord = GooglePlace.query.filter(GooglePlace.placeid == place.placeid).first()
            if gprecord:
                pluscode = gprecord.pluscode
            else:
                pluscode = ''
            thisplace = {
                'Name': placerecord.placename,
                'Distance': distance_between_places(self.myjob.lat, self.myjob.lng, self.getlat(gprecord), self.getlng(gprecord)),
                'Address': placerecord.vicinity,
                'Plus Code' : pluscode,
                'Latitude' : helper.get_location_from_placeid(placerecord.id)['lat'],
                'Longitude' : helper.get_location_from_placeid(placerecord.id)['lng'],
                'KeyWords': getKeywords(keywordsrecords),
                'Coffee': self.is_keyword_in_config_keywords(coffeetypes, keywordsrecords),
                'Licensed': self.is_keyword_in_config_keywords(licensedtypes, keywordsrecords),
                'Breakfast': self.is_open_for_meal(self.meals['breakfast'], self.meals['breakfastclose'], place.placeid),
                'Lunch': self.is_open_for_meal(self.meals['lunch'], self.meals['lunchclose'], place.placeid),
                'Dinner': self.is_open_for_meal(self.meals['dinner'], self.meals['dinnerclose'], place.placeid),
                'Late': self.is_open_for_meal(self.meals['supper'], self.meals['supperclose'], place.placeid),
                'Rating' : self.get_rating(gprecord),
                'Total Ratings' : self.get_total_ratings(gprecord),
                'Maps URL': self.get_map_url(gprecord),
                'Website': self.get_website(gprecord)
            }
            output.append(thisplace)
        return output

    def get_map_url(self,gprecord):
        if (gprecord is not None) and (gprecord.placeurl is not None):
            return gprecord.placeurl
        else:
            return ''

    def get_website(self, gprecord):
        if (gprecord is not None) and (gprecord.website is not None):
            return gprecord.website
        else:
            return ''

    def is_keyword_in_config_keywords(self, configkeywords, keywordsrecords):
        for configkeyword in configkeywords:
            for keywordrecord in keywordsrecords:
                if keywordrecord.placetype == configkeyword:
                    return 'Yes'
        return ''

    def getlat(self, gprecord):
        if gprecord is not None:
            if gprecord.lat is not None:
                return gprecord.lat
        else:
            return 0.0

    def getlng(self, gprecord):
        if gprecord is not None:
            if gprecord.lng is not None:
                return gprecord.lng
        return 0.0

    
    def is_open_for_meal(self, mealtime, mealtimeclose, placeid):
        mealtime = int(mealtime)
        mealtimeclose = int(mealtimeclose)
        openrecords = OpeningHours.query.filter(OpeningHours.placeid == placeid).first()
        if openrecords is None:
            return ''
        mydict = openrecords.__dict__
        mylistofdays = ('sunday','monday','tuesday','wednesday','thursday','friday','saturday')
        for myday in mylistofdays:
            if mydict[myday + 'open'] is None or mydict[myday + 'close'] is None:
                continue
            
            myopen = int(mydict[myday + 'open'])
            myclose = int(mydict[myday + 'close'])
            if myclose < myopen:
                myclose = 2359
            if (myopen < mealtimeclose) and (myclose > mealtime):
                return 'Yes'
        return ''


    def get_rating(self, record):
        if (record is not None) and (record.rating is not None):
            return record.rating
        else:
            return 0.0

    def get_total_ratings(self, record):
        output = 0
        if (record is not None) and (record.user_ratings_total is not None):
            output = record.user_ratings_total
        return output
    
class new_tar_report:
    mymeals = ('breakfast', 'lunch', 'dinner', 'supper',)
    def __init__(self, jobnumber):
        self.jobnumber = jobnumber
        self.meals = {}
        for meal in self.mymeals:
            self.meals[meal] = helper.getapikey(meal).replace(':', '')
            self.meals[meal + 'close'] = helper.getapikey(meal +'close').replace(':', '')
        self.myjob = JobList.query.filter(JobList.id == self.jobnumber).first()
        self.myplacesrecords = JobResults.query.filter(JobResults.jobid == self.jobnumber).all()
    
    def create_report(self):
        output = []

        coffeetypes = get_Keyword_type_list('coffee')
        licensedtypes = get_Keyword_type_list('license')

        for place in self.myplacesrecords:
            placerecord = Places.query.filter(Places.id == place.placeid).first()
            gprecord = GooglePlace.query.filter(GooglePlace.placeid == place.placeid).first() or GooglePlace(placeid=place, rating=0, user_ratings_total=0)
            keywordsrecords = KeyWords.query.filter(KeyWords.placeid == place.placeid).all()
            if gprecord:
                pluscode = gprecord.pluscode
            else:
                pluscode = ''
            thisplace = {
                'Name' : placerecord.placename,
                'Distance': rounded_distance_between_places(self.myjob.lat, self.myjob.lng, getlat(gprecord), getlng(gprecord)),
                'Address': placerecord.vicinity,
                'Plus Code' : pluscode,
                'Latitude' : helper.get_location_from_placeid(placerecord.id)['lat'],
                'Longitude' : helper.get_location_from_placeid(placerecord.id)['lng'],
                'Coffee': is_keyword_in_config_keywords(coffeetypes, keywordsrecords),
                'Licensed': is_keyword_in_config_keywords(licensedtypes, keywordsrecords),
                'Breakfast': is_open_for_meal(self.meals['breakfast'], self.meals['breakfastclose'], place.placeid),
                'Lunch': is_open_for_meal(self.meals['lunch'], self.meals['lunchclose'], place.placeid),
                'Dinner': is_open_for_meal(self.meals['dinner'], self.meals['dinnerclose'], place.placeid),
                'Late': is_open_for_meal(self.meals['supper'], self.meals['supperclose'], place.placeid),
                'Google Rating' : gprecord.rating,
                'Google User Ratings' : gprecord.user_ratings_total,
                'Subjective Price Level' : get_price_level((gprecord,)),
                'KeyWords': getKeywords(keywordsrecords)
            }
            output.append(thisplace)
        return output

