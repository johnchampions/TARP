from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.annotation import EMPTY_ANNOTATIONS
from sqlalchemy.sql.expression import column, text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import FLOAT, Boolean, DateTime, Float, TEXT
from flasky.db2 import Base
from datetime import datetime

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(150))
    email = Column(String(120))
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    profile_url = Column(String, nullable=False)
    access_token = Column(String, nullable=False)

    def __init__(self, username=None, password=None, email=None):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f'<User {self.username}!r>'

class ConfigKeys(Base):
    __tablename__ = 'configkeys'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    keyname = Column(String(50), unique=True)
    keyvalue = Column(TEXT)
    keytype = Column(String(20))

    def __init__(self, keyname=None, keyvalue=None, keytype=None):
        self.keyname = keyname
        self.keyvalue = keyvalue
        self.keytype = keytype

    def __repr__(self):
       return f'<KeyName {self.keyname!r}, KeyValue {self.keyvalue!r}>'

class KeyWords(Base):
    __tablename__ = 'types'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('places.id'))
    placetype = Column(TEXT)
        
    def __init__(self, placeid=None, placetype=None):
        self.placeid = placeid
        self.placetype = placetype

class Places(Base):
    __tablename__= 'places'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placename = Column(TEXT(collation='utf8mb4'))
    parentplace = Column(Integer)
    googleplaceid = Column(Integer, ForeignKey('googleplace.id'))
    yelpplaceid = Column(Integer, ForeignKey('yelpplace.id'))
    zomatoplaceid = Column(Integer, ForeignKey('zomatoplace.id'))
    vicinity = Column(TEXT)
    street1 = Column(TEXT)
    street2 = Column(TEXT)
    suburb = Column(TEXT)
    postcode = Column(TEXT)
    placestate = Column(TEXT)
    phonenumber = Column(TEXT)

    def __init__(self, placename=None, parentplace=None, googleplaceid=None, 
            yelpplaceid=None, zomatoplaceid=None, vicinity=None, street1=None, street2=None,
            suburb=None, postcode=None, placestate=None, phonenumber=None):
        self.placename = placename
        self.parentplace = parentplace
        self.googleplaceid = googleplaceid
        self.yelpplaceid = yelpplaceid
        self.zomatoplaceid = zomatoplaceid
        self.vicinity = vicinity
        self.street1 = street1
        self.street2 = street2
        self.suburb = suburb
        self.postcode = postcode
        self.placestate = placestate
        self.phonenumber = phonenumber
    
class GooglePlace(Base):
    __tablename__ = 'googleplace'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('places.id'))
    business_status = Column(Integer)
    viewportnelat = Column(FLOAT)
    viewportnelng = Column(FLOAT)
    viewportswlat = Column(FLOAT)
    viewportswlng = Column(FLOAT)
    lat = Column(FLOAT)
    lng = Column(FLOAT)
    price_level = Column(Integer)
    rating = Column(FLOAT)
    user_ratings_total = Column(Integer)
    googleplace_id = Column(TEXT)
    placeurl = Column(TEXT)
    website = Column(TEXT)

    def __init__(self, placeid=None, business_status=None, viewportnelat=None,
            viewportnelng=None, viewportswlat=None, viewportswlng=None, 
            lat=None, lng=None, price_level=None, rating=None,
            user_ratings_total=None, googleplace_id=None, placeurl=None, 
            website=None):
        self.placeid = placeid
        self.business_status = business_status
        self.viewportnelat = viewportnelat
        self.viewportnelng = viewportnelng
        self.viewportswlat = viewportswlat
        self.viewportswlng = viewportswlng
        self.lat = lat
        self.lng = lng
        self.price_level = price_level
        self.rating = rating
        self.user_ratings_total = user_ratings_total
        self.googleplace_id = googleplace_id
        self.placeurl = placeurl
        self.website = website


class YelpPlace(Base):
    __tablename__ = 'yelpplace'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('places.id'))
    business_status = Column(Integer)
    lat = Column(FLOAT)
    lng = Column(FLOAT)
    price_level = Column(Integer)
    rating = Column(FLOAT)
    user_ratings_total = Column(Integer)
    yelpplace_id = Column(TEXT)
    website = Column(TEXT)
    
    def __init__(self, placeid=None, business_status=None, lat=None, lng=None,
            price_level=None, rating=None, user_ratings_total=None, 
            yelpplace_id=None, website=None):
        self.placeid = placeid
        self.business_status = business_status
        self.lat = lat
        self.lng = lng
        self.price_level = price_level
        self.rating = rating
        self.user_ratings_total = user_ratings_total
        self.yelpplace_id = yelpplace_id
        self.website = website

class ZomatoPlace(Base):
    __tablename__ = 'zomatoplace'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('places.id'))
    zomatoplace_id = Column(Integer)
    rating = Column(FLOAT)
    user_ratings_total = Column(Integer)
    cuisine = Column(TEXT)
    website =  Column(TEXT)
    business_status = Column(Integer)
    price_level = Column(Integer)
    lat = Column(FLOAT)
    lng = Column(FLOAT)

    def __init__(self, 
            placeid=None, 
            zomatoplace_id=None,
            rating=None,
            user_rating_total=None,
            cuisine=None,
            website=None,
            business_status=None,
            price_level=None,
            lat=None,
            lng=None):
        self.placeid = placeid
        self.zomatoplace_id = zomatoplace_id
        self.rating = rating
        self.user_ratings_total = user_rating_total
        self.cuisine = cuisine
        self.website = website
        self.business_status = business_status
        self.price_level = price_level
        self.lat = lat
        self.lng = lng


class OpeningHours(Base):
    __tablename__ = 'openinghours'
    __table_args__ = {'extend_existing': True }
    __mapper_args__ = {'confirm_deleted_rows': True }
    
    id = Column(Integer, primary_key=True)
    placeid =Column(Integer, ForeignKey('places.id'))
    sundayopen = Column(TEXT)
    sundayclose = Column(TEXT)
    mondayopen = Column(TEXT)
    mondayclose = Column(TEXT)
    tuesdayopen = Column(TEXT)
    tuesdayclose = Column(TEXT)
    wednesdayopen = Column(TEXT)
    wednesdayclose = Column(TEXT)
    thursdayopen = Column(TEXT)
    thursdayclose = Column(TEXT)
    fridayopen = Column(TEXT)
    fridayclose = Column(TEXT)
    saturdayopen = Column(TEXT)
    saturdayclose = Column(TEXT)

    def __init__(self, placeid=None, sundayopen=None, sundayclose=None,
            mondayopen=None, mondayclose=None, tuesdayopen=None, tuesdayclose=None,
            wednesdayopen=None, wednesdayclose=None, thursdayopen=None, thursdayclose=None,
            fridayopen=None, fridayclose=None, saturdayopen=None, saturdayclose=None):
        self.placeid =placeid
        self.sundayopen = sundayopen
        self.sundayclose = sundayclose
        self.mondayopen = mondayopen
        self.mondayclose = mondayclose
        self.tuesdayopen = tuesdayopen
        self.tuesdayclose = tuesdayclose
        self.wednesdayopen = wednesdayopen
        self.wednesdayclose = wednesdayclose
        self.thursdayopen = thursdayopen
        self.thursdayclose = thursdayclose
        self.fridayopen = fridayopen
        self.fridayclose = fridayclose
        self.saturdayopen = saturdayopen
        self.saturdayclose = saturdayclose

class Reviews(Base):
    __tablename__ = 'reviews'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('places.id'))
    rating = Column(Integer)
    reviewtext = Column(TEXT)
    source = Column(TEXT)

    def __init__(self, placeid=None, rating=None, reviewtext=None, source=None):
        self.placeid = placeid
        self.rating = rating
        self.reviewtext = reviewtext
        self.source = source

    
class JobList(Base):
    __tablename__ = 'joblist'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    jobjson = Column(TEXT)
    jobtype = Column(TEXT)
    address = Column(TEXT)
    radius = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)
    maxprice = Column(Integer)
    minprice = Column(Integer)
    roughcount = Column(Integer)

    def __init__(self, jobjson=None, jobtype=None, address=None, radius=None, lat=None, lng=None,
        maxprice=None, minprice=None, roughcount=None):
        self.jobjson = jobjson
        self.jobtype = jobtype
        self.address = address
        self.radius = radius
        self.lat = lat
        self.lng = lng
        self.maxprice = maxprice
        self.minprice = minprice
        self.roughcount = roughcount


class PostCode(Base):
    __tablename__ = 'postcode'
    __table_args__ = {'extend_existing': True}
    postcode = Column(Integer)
    Locality = Column(TEXT)
    postcodestate = Column(TEXT)
    lat = Column(Float)
    lng = Column(Float)
    sa2 = Column(TEXT)
    ID = Column(Integer, primary_key=True)

    def __init__(self, postcode=None, locality=None, postcodestate=None, lat=None, lng=None, sa2=None):
        self.postcode = postcode
        self.Locality = locality
        self.postcodestate = postcodestate
        self.lat = lat
        self.lng = lng
        self.sa2 = sa2

class JobResults(Base):
    __tablename__ = 'jobresults'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('places.id'))
    jobid = Column(Integer, ForeignKey('joblist.id'))

    def __init__(self, placeid=None, jobid=None):
        self.placeid = placeid
        self.jobid = jobid

class SearchCategories(Base):
    __tablename__ = 'SearchCategories'
    __table_args__ = {'extend_existing': True }
    id = Column(Integer, primary_key=True)
    jobid = Column(Integer, ForeignKey('joblist.id'))
    category = Column(TEXT)
    plugin = Column(TEXT)

    def __init__(self, jobid=None, category=None, plugin=None):
        self.jobid = jobid
        self.category = category
        self.plugin = plugin


class CuisineList(Base):
    __tablename__ = 'cuisinelist'
    __table_args__ = {'extend_existing': True }
    id = Column(Integer, primary_key=True)
    placetype = Column(TEXT)
    coffee = Column(Boolean)
    license = Column(Boolean)
    cuisine = Column(Boolean)
    blacklist = Column(Boolean)

    def __init__(self, 
            placetype=None,
            coffee=None,
            license=None,
            cuisine=None,
            blacklist=None):
        self.placetype = placetype
        self.coffee = coffee
        self.license = license
        self.cuisine = cuisine
        self.blacklist = blacklist
