from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.sql.schema import ForeignKey
from .db import Base


class ConfigKeys(Base):
    __tablename__ = 'configkeys'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    keyname = Column(String(50), unique=True)
    keyvalue = Column(String)
    keytype = Column(String(20))

    def __init__(self, keyname=None, keyvalue=None, keytype='string'):
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
    placetype = Column(String)
    
    def __init__(self, placeid=None, placetype=None):
        self.placeid = placeid
        self.placetype = placetype

class Places(Base):
    __tablename__= 'places'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placename = Column(String(collation='utf8mb4'))
    parentplace = Column(Integer)
    googleplaceid = Column(Integer, ForeignKey('googleplace.id'))
    yelpplaceid = Column(Integer, ForeignKey('yelpplace.id'))
    zomatoplaceid = Column(Integer, ForeignKey('zomatoplace.id'))
    vicinity = Column(String)
    street1 = Column(String)
    street2 = Column(String)
    suburb = Column(String)
    postcode = Column(String)
    placestate = Column(String)
    phonenumber = Column(String)
    pluscode = Column(String)

    def __init__(self, placename=None, parentplace=None, googleplaceid=None, 
            yelpplaceid=None, zomatoplaceid=None, vicinity=None, street1=None, street2=None,
            suburb=None, postcode=None, placestate=None, phonenumber=None, pluscode=None):
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
        self.pluscode = pluscode
    
class GooglePlace(Base):
    __tablename__ = 'googleplace'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('places.id'))
    business_status = Column(Integer)
    viewportnelat = Column(Float)
    viewportnelng = Column(Float)
    viewportswlat = Column(Float)
    viewportswlng = Column(Float)
    lat = Column(Float)
    lng = Column(Float)
    price_level = Column(Integer)
    rating = Column(Float)
    user_ratings_total = Column(Integer)
    googleplace_id = Column(String)
    placeurl = Column(String)
    website = Column(String)
    pluscode = Column(String)

    def __init__(self, placeid=None, business_status=None, viewportnelat=None,
            viewportnelng=None, viewportswlat=None, viewportswlng=None, 
            lat=None, lng=None, price_level=None, rating=None,
            user_ratings_total=None, googleplace_id=None, placeurl=None, 
            website=None, pluscode=None):
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
        self.pluscode = pluscode


class YelpPlace(Base):
    __tablename__ = 'yelpplace'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('places.id'))
    business_status = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)
    price_level = Column(Integer)
    rating = Column(Float)
    user_ratings_total = Column(Integer)
    yelpplace_id = Column(String)
    website = Column(String)
    
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
    rating = Column(Float)
    user_ratings_total = Column(Integer)
    cuisine = Column(String)
    website =  Column(String)
    business_status = Column(Integer)
    price_level = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)

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
    sundayopen = Column(String)
    sundayclose = Column(String)
    mondayopen = Column(String)
    mondayclose = Column(String)
    tuesdayopen = Column(String)
    tuesdayclose = Column(String)
    wednesdayopen = Column(String)
    wednesdayclose = Column(String)
    thursdayopen = Column(String)
    thursdayclose = Column(String)
    fridayopen = Column(String)
    fridayclose = Column(String)
    saturdayopen = Column(String)
    saturdayclose = Column(String)

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
    reviewString = Column(String)
    source = Column(String)

    def __init__(self, placeid=None, rating=None, reviewString=None, source=None):
        self.placeid = placeid
        self.rating = rating
        self.reviewString = reviewString
        self.source = source

    
class JobList(Base):
    __tablename__ = 'joblist'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    jobjson = Column(String)
    jobtype = Column(String)
    address = Column(String)
    radius = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)
    maxprice = Column(Integer)
    minprice = Column(Integer)
    roughcount = Column(Integer)
    googleplugin = Column(Integer)
    yelpplugin = Column(Integer)
    zomatoplugin = Column(Integer)
    googlecomplete = Column(Boolean)
    yelpcomplete = Column(Boolean)
    zomatocomplete = Column(Boolean)
    userid = Column(Integer)

    def __init__(self, jobjson=None, jobtype=None, address=None, radius=None, lat=None, lng=None,
        maxprice=None, minprice=None, roughcount=None, userid=None, googleplugin=0, yelpplugin=0,
        zomatoplugin=0, googlecomplete=False, yelpcomplete=False, zomatocomplete=False):
        self.jobjson = jobjson
        self.jobtype = jobtype
        self.address = address
        self.radius = radius
        self.lat = lat
        self.lng = lng
        self.maxprice = maxprice
        self.minprice = minprice
        self.roughcount = roughcount
        self.userid = userid
        self.googleplugin = googleplugin
        self.googlecomplete = googlecomplete
        self.yelpplugin = yelpplugin
        self.yelpcomplete = yelpcomplete
        self.zomatoplugin = zomatoplugin
        self.zomatocomplete = zomatocomplete


class PostCode(Base):
    __tablename__ = 'postcode'
    __table_args__ = {'extend_existing': True}
    postcode = Column(Integer)
    Locality = Column(String)
    postcodestate = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    sa2 = Column(String)
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
    __tablename__ = 'searchcategories'
    __table_args__ = {'extend_existing': True }
    id = Column(Integer, primary_key=True)
    jobid = Column(Integer, ForeignKey('joblist.id'))
    category = Column(String)
    plugin = Column(String)

    def __init__(self, jobid=None, category=None, plugin=None):
        self.jobid = jobid
        self.category = category
        self.plugin = plugin

class RegionData(Base):
    __tablename__ = 'regiondata'
    __table_args__ = {'extend_existing': True }
    id = Column(Integer, primary_key=True)
    sa2_maincode = Column(String(9))
    sa2_5_digit = Column(String(5))
    sa2_name = Column(String)
    sa3_name = Column(String)
    sa4_name = Column(String)
    state = Column(String)
    area = Column(Float)

    def __init__(self, sa2_maincode = None,
            sa2_5_digit = None,
            sa2_name = None,
            sa3_name = None,
            sa4_name = None,
            state = None,
            area = None):
        self.sa2_maincode = str(sa2_maincode)[:9]
        self.sa2_5_digit = str(sa2_5_digit)[:5]
        self.sa2_name = str(sa2_name)
        self.sa3_name = sa3_name
        self.sa4_name = sa4_name
        self.state = state
        self.area = area

class Polygon(Base):
    __tablename__ = 'polygon'
    __table_args__ = {'extend_existing': True }
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('regiondata.id'))
    max_lng = Column(Float)
    max_lat = Column(Float)
    min_lng = Column(Float)
    min_lat = Column(Float)
    points = Column(Integer)

    def __init__(self,
            region_id=None,
            max_lng=None,
            max_lat=None,
            min_lng=None,
            min_lat=None,
            points=None):
        self.region_id = region_id
        self.max_lng = max_lng
        self.max_lat = max_lat
        self.min_lng = min_lng
        self.min_lat = min_lat
        self.points = points

class PointList(Base):
    __tablename__ = 'pointlist'
    __table_args__ = {'extend_existing': True }
    id = Column(Integer, primary_key=True)
    polygon_id = Column(Integer, ForeignKey('polygon.id'))
    lat = Column(Float)
    lng = Column(Float)
    order = Column(Integer)

    def __init__(self,
            polygon_id=None,
            lat=None,
            lng=None,
            order=None):
        self.polygon_id = polygon_id
        self.lat = float(lat)
        self.lng = float(lng)
        self.order = int(order)

class LineList(Base):
    __tablename__ = 'linelist'
    __table_args__ = {'extend_existing': True }
    id = Column(Integer, primary_key=True)
    polygon_id = Column(Integer, ForeignKey('polygon.id'))
    nlat = Column(Float)
    nlng = Column(Float)
    slat = Column(Float)
    slng = Column(Float)
    
    def __init__(self,
            polygon_id=None,
            nlat=None,
            nlng=None,
            slat=None,
            slng=None):
        self.polygon_id = polygon_id
        self.nlat = nlat
        self.nlng = nlng
        self.slat = slat
        self.slng = slng


class CuisineList(Base):
    __tablename__ = 'cuisinelist'
    __table_args__ = {'extend_existing': True }
    id = Column(Integer, primary_key=True)
    placetype = Column(String)
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


class CategoryList(Base):
    __tablename__ = 'categorylist'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    comment = Column(String)

    def __init__(self,
            name=None,
            comment=None):
        self.name = name
        self.comment = comment

class CategoryToType(Base):
    __tablename__ = 'categorytotype'
    id = Column(Integer, primary_key=True)
    categoryid = Column(Integer, ForeignKey('categorylist.id', ondelete='CASCADE'))
    cuisineid = Column(Integer, ForeignKey('cuisinelist.id', ondelete='CASCADE'))

    def __init__(self,
            categoryid=None,
            cuisineid=None):
        self.categoryid = categoryid
        self.cuisineid = cuisineid

class GoogleSupportedTypes(Base):
    __tablename__ = 'googlesupportedtypes'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    value = Column(String)
    checked = (Boolean)

    def __init__(self,
                description=None,
                value=None,
                checked=True):
        self.description = description
        self.value = value
        self.checked = checked


