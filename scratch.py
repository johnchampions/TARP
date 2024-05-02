import random
import string

from flask_user.decorators import _is_logged_in_with_confirmed_email
from flasky.models import GooglePlace, Places
from flasky.db import db_session
from flasky.tar_helper import get_pluscode_from_placeid

def get_random_string(length):
    letters = string.ascii_letters + string.digits
    apistring = ''.join(random.choice(letters) for i in range(length))
    return apistring

def fixplacerecords():
    all_place_records = Places.query.all()
    for place_record in all_place_records:
        place_record.pluscode = get_pluscode_from_placeid(place_record.id)
        db_session.commit()
        print(', '.join((place_record.placename, place_record.pluscode)))

if __name__ == '__main__':
    fixplacerecords()
    