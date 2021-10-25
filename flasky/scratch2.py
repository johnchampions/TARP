from models import JobList, JobResults, OpeningHours, SearchCategories
from db2 import db_session
import json
timefields = ('sundayopen','sundayclose',
    'mondayopen','mondayclose',
    'tuesdayopen','tuesdayclose',
    'wednesdayopen','wednesdayclose',
    'thursdayopen','thursdayclose',
    'fridayopen','fridayclose',
    'saturdayopen','saturdayclose',
)

def clean_opening_hours():
    OpeningHours.__mapper_args__['confirm_deleted_rows'] = False
    ohrecords = OpeningHours.query.filter().all()
    for record in ohrecords:
        recorddict = record.__dict__
        delthisrecord = True
        for timefield in timefields:
            if recorddict[timefield] is not None:
                delthisrecord = False
                break
        if delthisrecord:
            db_session.delete(record)
            print( 'Deleted: ' + record)
    db_session.commit()
    OpeningHours.__mapper_args__['confirm_deleted_rows'] = True


def rejigger_job_list():
    joblistrecords = JobList.query.all()
    for joblistrecord in joblistrecords:
        jobjson = json.loads(joblistrecord.jobjson)
        joblistrecord.address = jobjson['address']
        joblistrecord.radius = jobjson['radius']
        joblistrecord.lat = jobjson['lat']
        joblistrecord.lng = jobjson['lng']
        joblistrecord.maxprice = jobjson['maxprice']
        joblistrecord.minprice = jobjson['minprice']
        for place in jobjson['placelist']:
            jobresult = JobResults(placeid=place, jobid=joblistrecord.id)
            db_session.add(jobresult)
        for searchcategory in jobjson['types']:
            searchcategoryrecord = SearchCategories(jobid=joblistrecord.id, category=searchcategory, plugin='googletype')
            db_session.add(searchcategoryrecord)
        for searchcategory in jobjson['categories']:
            searchcategoryrecord = SearchCategories(jobid=joblistrecord.id, category=searchcategory, plugin='yelpcategory')
            db_session.add(searchcategoryrecord)
    db_session.commit




        
