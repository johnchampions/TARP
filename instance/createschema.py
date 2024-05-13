from sqlalchemy import MetaData, Table, Column, Integer, String, Float, Boolean, ForeignKey, create_engine
from flasky.db import engine, db_session
from flasky.models import GoogleSupportedTypes, ConfigKeys

def create_database():

    meta = MetaData()

    ConfigKeys = Table(
        'configkeys', meta,
        Column('id', Integer, primary_key=True),
        Column('keyname', String, unique=True),
        Column('keyvalue', String),
        Column('keytype', String)
    )

    KeyWords = Table(
        'types', meta,
        Column('id', Integer, primary_key=True),
        Column('placeid', Integer, ForeignKey('places.id')),
        Column('placetype', String)
    )

    Places = Table(
        'places', meta,
        Column('id', Integer, primary_key=True),
        Column('placename', String),
        Column('parentplace', Integer, ForeignKey('places.id')),
        Column('googleplaceid', Integer, ForeignKey('googleplace.id')),
        Column('vicinity', String),
        Column('street1', String),
        Column('street2', String),
        Column('suburb', String),
        Column('postcode', String),
        Column('placestate', String),
        Column('phonenumber', String),
        Column('pluscode', String)
    )

    GooglePlace = Table(
        'googleplace', meta,
        Column('id', Integer, primary_key=True),
        Column('placeid', Integer, ForeignKey('places.id')),
        Column('business_status',Integer),
        Column('viewportnelat', Float),
        Column('viewportnelng', Float),
        Column('viewportswlat',Float),
        Column('viewportswlng', Float),
        Column('lat', Float),
        Column('lng', Float),
        Column('price_level', Integer),
        Column('rating', Float),
        Column('user_ratings_total', Integer),
        Column('googleplace_id', String),
        Column('placeurl', String),
        Column('website', String),
        Column('pluscode', String),
    )

    OpeningHours = Table(
        'openinghours', meta,
        Column('id', Integer, primary_key=True),
        Column('placeid', Integer, ForeignKey('places.id', ondelete='CASCADE')),
        Column('sundayopen', String), 
        Column('sundayclose', String),
        Column('mondayopen', String), 
        Column('mondayclose', String),
        Column('tuesdayopen', String),
        Column('tuesdayclose', String),
        Column('wednesdayopen', String),
        Column('wednesdayclose', String),
        Column('thursdayopen', String), 
        Column('thursdayclose', String),
        Column('fridayopen', String),
        Column('fridayclose', String), 
        Column('saturdayopen', String),
        Column('saturdayclose', String)
        )

    Reviews = Table(
        'reviews', meta,
        Column('id', Integer, primary_key=True),
        Column('placeid', Integer, ForeignKey('places.id', ondelete='CASCADE')),
        Column('rating',Integer),
        Column('reviewtext',String),
        Column('source', String)
    )

    JobList = Table(
        'joblist', meta,
        Column('id', Integer, primary_key=True),
        Column('jobjson', String),
        Column('jobtype', String),
        Column('address', String),
        Column('radius', Integer),
        Column('lat', Float),
        Column('lng', Float),
        Column('maxprice', Integer),
        Column('minprice', Integer),
        Column('roughcount', Integer),
        Column('googleplugin', Integer),
        Column('yelpplugin', Integer),
        Column('zomatoplugin', Integer),
        Column('googlecomplete', Boolean),
        Column('yelpcomplete', Boolean),
        Column('zomatocomplete', Boolean),
        Column('userid', Integer)
    )

    PostCode = Table(
        'postcode', meta,
        Column('postcode', Integer),
        Column('Locality', String),
        Column('postcodestate', String),
        Column('lat', Float),
        Column('lng', Float),
        Column('sa2', String),
        Column('ID', Integer, primary_key=True)
    )

    JobResults = Table(
        'jobresults', meta,
        Column('id', Integer, primary_key=True),
        Column('placeid', Integer, ForeignKey('places.id')),
        Column('jobid', Integer, ForeignKey('joblist.id'))
    )

    SearchCategories = Table(
        'searchcategories', meta,
        Column('id', Integer, primary_key=True),
        Column('jobid', Integer, ForeignKey('joblist.id')),
        Column('category', String),
        Column('plugin', String)
    )

    RegionData = Table(
        'regiondata', meta,
        Column('id', Integer, primary_key=True),
        Column('sa2_maincode', String),
        Column('sa2_5_digit', String),
        Column('sa2_name', String),
        Column('sa3_name', String),
        Column('sa4_name', String),
        Column('state', String),
        Column('area', Float),
    )

    Polygon = Table(
        'polygon', meta,
        Column('id', Integer, primary_key=True),
        Column('region_id', Integer, ForeignKey('regiondata.id')),
        Column('max_lng', Float),
        Column('max_lat', Float),
        Column('min_lng', Float),
        Column('min_lat', Float),
        Column('points', Integer)
    )

    PointList = Table(
        'pointlist', meta,
        Column('id', Integer, primary_key=True),
        Column('polygon_id', Integer, ForeignKey('polygon.id')),
        Column('lat', Float),
        Column('lng', Float),
        Column('order', Integer),
    )

    LineList = Table(
        'linelist', meta,
        Column('id', Integer, primary_key=True),
        Column('polygon_id', Integer, ForeignKey('polygon.id')),
        Column('nlat', Float),
        Column('nlng', Float),
        Column('slat', Float),
        Column('slng', Float)
    )

    CuisineList = Table(
        'cuisinelist', meta,
        Column('id', Integer, primary_key=True),
        Column('placetype', String),
        Column('coffee', Boolean),
        Column('license', Boolean),
        Column('cuisine', Boolean),
        Column('blacklist', Boolean)
    )

    CategoryList = Table(
        'categorylist', meta,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('comment', String)
    )

    CategoryToType = Table(
        'categorytotype', meta,
        Column('id', Integer, primary_key=True),
        Column('categoryid', Integer, ForeignKey('categorylist.id', ondelete='CASCADE')),
        Column('cuisineid', Integer, ForeignKey('cuisinelist.id', ondelete='CASCADE'))
    )

    GoogleSupportedTypes = Table(
        'googlesupportedtypes', meta,
        Column('id', Integer, primary_key=True),
        Column('description', String),
        Column('value', String),
        Column('checked', Boolean)
    )
    meta.create_all(engine)
    
    myInsert = ConfigKeys(keyname='googleapikey', keyvalue='AIzaSyCG6S55TX0YlfBGrnyFlBEMrQzwpBdICzU', keytype='string')
    db_session.add(myInsert)

    dictlist = {
        'airport': 'Airport',
        'amusement_park': 'Amusement Park',
        'aquarium': 'Aquarium',
        'art_gallery': 'Art Gallery',
        'bakery': 'Bakery',
        'bar': 'Bar',
        'bowling_alley': 'Bowling Alley',
        'cafe': 'Cafe',
        'casino': 'Casino',
        'convenience_store': 'Convenience Store',
        'gas_station': 'Gas Station',
        'liquor_store': 'Liquor Store',
        'lodging': 'Lodging',
        'meal_delivery': 'Mwal Delivery',
        'meal_takeaway': 'Meal Takeaway',
        'night_club': 'Night Club',
        'restaurant': 'Restaurant',
        'shopping_mall': 'Shopping Mall',
        'spa': 'Spa',
        'stadium': 'Stadium',
        'supermarket': 'Supermarket'    
    }

    for i in dictlist:
        myInsert = GoogleSupportedTypes(value = i, description = dictlist[i])
        db_session.add(myInsert)
        db_session.commit()

if __name__ == "__main__":
    create_database()
