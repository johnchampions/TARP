import requests
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service

from time import sleep
from bs4 import BeautifulSoup
import flasky.gs as gs
import config
from flasky.tar_helper import add_type_to_place
from re import search
from flasky.models import ZomatoPlace, Places, OpeningHours, JobResults, JobList
from flasky.db import db_session
from openlocationcode import openlocationcode
import config

headers = { 
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'accept-encoding' : 'gzip, deflate, br',
    'accept-language' : 'en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,gd;q=0.6',
    'sec-ch-ua' : '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest' : 'document',
    'sec-fetch-mode' : 'navigate',
    'sec-fetch-site' : 'none',
    'sec-fetch-user' : '?1',
    'cache-control' : 'no-cache',
    'pragma' : 'no-cache',
    'upgrade-insecure-requests' : '1',
    'scheme' : 'https',
    'connection' : 'keep-alive'
    }


url = "https://www.zomato.com/"

def data_from_url(path, params=None):
    if params is None:
        try:
                response = requests.get(path, headers=headers, timeout=10)
        except:
            return dict()
    else:
        try:
            response = requests.get(path, params=params, headers=headers,timeout=10)
        except:
            return dict()
    return get_preload_json(response.text)

def get_job_list(keymatch):
    #TODO: add thesevalues
    
    url = f'{config.URL}joblist/zomjob/{keymatch}'
    response = requests.get(url, timeout=10)
    return json.loads(response.text.encode('UTF-8'))


def get_preload_json(page_text):
    soup = BeautifulSoup(page_text, 'html.parser')
    s = soup.find_all('script')
    for myscript in s:
        mystring = str(myscript.string)
        if mystring.strip().startswith('window.__PRELOADED_STATE__ = JSON.parse'):
            mystring = mystring.strip()
            mystring = mystring.replace('window.__PRELOADED_STATE__ = JSON.parse("', '')
            mystring = mystring.replace('\\"', '"')
            mystring = mystring[:-3]
            mystring = mystring.replace('\\\\u003c', '<')
            mystring = mystring.replace('\\\\"', '\\"')
            mystring = mystring.replace('\\\\\\\\\\\"', '\\\\\\"')
            return json.loads(mystring)
    return {}


class zomatosearch:
    zomatoidlist = []
    placeidlist = []
    def __init__(self, location, radius, address, keyword=''):
        print("Hello from zs")
        self.radius = radius
        self.keyword = keyword
        self.location = location
        self.address = address
        self.zomatoidlist = self.nearby_places()
        
    
    def get_zomatoidlist(self):
        if self.zomatoidlist is None:
            return []
        return self.zomatoidlist

    def nearby_places(self):
        print('sz.nearby_places')
        params = {
            'radius' : str(self.radius),
            'latitude' : str(self.location['lat']),
            'longitude' : str(self.location['lng']),
        }
        if self.keyword != '':
            params['term'] = self.keyword
        linklist = self.selenium_get(url)
        return linklist

    def selenium_get(self, url):
        print('selenium_get')
        chrome_options = Options()
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--user-agent="' + headers['User-agent'] + '"')
        print('selenium_get before driver')
        driver = webdriver.Chrome('chromedriver', options=chrome_options)
        print('selenium_get driver')
        map_coordinates = {'latitude': self.location['lat'],
            'longitude': self.location['lng'],
            'accuracy': 50}
        driver.execute_cdp_cmd('Browser.grantPermissions', {'origin': url, 'permissions': ['geolocation']},)
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", map_coordinates)
        try:
            driver.delete_all_cookies()
            driver.get(url)
        except:
            print('zomato connection error')
            driver.quit()
            return []
        try:

            addressbox = driver.find_element(By.XPATH, "//input[1]")
            addressbox.click()
            sleep(1)
            addressbox.send_keys(Keys.ARROW_DOWN)
            addressbox.send_keys(Keys.ENTER)
            sleep(1)
            dineout = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[4]/div[1]/div/div[2]/a")
            dineout.click()
            sleep(1)
            Filters = driver.find_element(By.XPATH, "(//*[contains(text(), 'Filters')] | //*[@value='Filters'])")
            Filters.click()
            sleep(1)
            sort_by_distance = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/section[2]/article/section[2]/div/section/section[5]/label/span')
            sort_by_distance.click()
            sleep(1)
            apply = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/section[2]/section/div/button[2]")
            apply.click()
            sleep(1)
        except:
            print('zomato interaction error')
            print(driver.page_source)
            driver.quit()
            return []
        can_scroll = True
        last_height = driver.execute_script("return document.body.scrollHeight")
        sleep(3)
        while can_scroll:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                can_scroll = False
            last_height = new_height
        page_source = driver.page_source
        driver.quit()
        return self.get_cards(page_source)

    def get_cards(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        s = soup.find_all('div', class_='jumbo-tracker')
        output = []
        for div in s:
            distance = div.find_all("p")[0].text
            link = div.find_all('a')[0]['href']
            if self.returnintmeters(distance) < int(self.radius):
                output.append(link)
        return output

    def returnintmeters(self,mystring):
        if mystring.split(' ')[1] == 'm':
            return int(mystring.split(' ')[0])
        if mystring.split(' ')[1] == 'km':
            myint = float(mystring.split(' ')[0]) * 1000
            return int(myint)

    def getplaceidlist(self, jobnumber=0):
        #if len(self.placeidlist) > 0:

        #    return self.placeidlist
        if self.zomatoidlist is None:
            return []
        for zomatoid in self.zomatoidlist:
            myzomatoplace = zomatoplace(zomatoid)
            myzomatoplace.get_zomatoplaceid()
            self.placeidlist.append(myzomatoplace.get_placeid())
            myzomatoplace.set_keywords()
            myzomatoplace.opening_hours_to_db()
            myzomatoplace.set_jobnumber(jobnumber)
            mygooglesearch = gs.googlesearch(myzomatoplace.get_location(),100,[], myzomatoplace.get_placename())
            if len(mygooglesearch.get_googleidlist()) != 0:
                mygoogleplace = gs.googleplace(mygooglesearch.get_googleidlist()[0])
                mygoogleplace.set_placeid(myzomatoplace.get_placeid())
                mygoogleplace.set_categories()
        myjob = JobList.query.filter(JobList.id == jobnumber).first()
        myjob.zomatocomplete = True
        db_session.commit()
        return self.placeidlist


class zomatoplace:
    placeid = 0
    zomatoplaceid = 0
    zomatoid =''
    jobnumber = int()
    location = dict()
    zomatoplacerecord = ZomatoPlace()
    placerecord = Places()
    myjson = dict()

    def __init__(self, zomatoid):
        self.zomatoid = zomatoid
        self.myjson = self.get_place_details()

    def get_zomatoplaceid(self):
        if self.zomatoplaceid == 0:
            self.set_zomatoplaceid()
        return self.zomatoplaceid

    def set_zomatoplaceid(self):
        myurl = url + self.zomatoid[1:]
        self.zomatoplacerecord = ZomatoPlace.query.filter(ZomatoPlace.website == myurl).first()
        if self.zomatoplacerecord is not None:
            return self.zomatoplacerecord.id
        if (self.myjson is None) or ('pages' not in self.myjson):
            self.zomatoplaceid  = 0
            return
        zomatoplace_id=self.myjson['pages']['current']['resId']
        rating = float(self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['rating']['aggregate_rating'])
        user_rating_total = int(self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['rating']['votes'])
        cuisine = self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['cuisine_string']
        website = myurl
        business_status = self.get_business_status(self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO'])
        price_level = self.get_price_level(self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_DETAILS']['CFT_DETAILS']['cfts'])
        lat = float(self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['latitude'])
        lng = float(self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['longitude'])
        self.zomatoplacerecord = ZomatoPlace(
            zomatoplace_id=zomatoplace_id,
            rating=rating,
            user_rating_total=user_rating_total,
            cuisine=cuisine,
            website=website,
            business_status= business_status,
            price_level=price_level,
            lat=lat,
            lng=lng)
        db_session.add(self.zomatoplacerecord)
        db_session.commit()
        self.zomatoplaceid = self.zomatoplacerecord.id

    def get_placeid(self):
        if self.placeid > 0:
            return self.placeid
        if (self.zomatoplacerecord is None) or (self.zomatoplacerecord.placeid is None):
            self.set_placeid()
        else:
            self.placeid = self.zomatoplacerecord.placeid
        return self.placeid

    def set_placeid(self, placeid=0):
        self.placerecord = Places.query.filter(Places.id == placeid).first()
        if (self.placerecord is None) and (self.myjson is not None) and (len(self.myjson) > 0):
            zomatoplace_id=self.myjson['pages']['current']['resId']
            place_name = self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['name']
            phone_number = self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['phoneDetails']['phoneStr']
            post_code = self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['zipcode']
            vicinity = self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['address']
            street1 = vicinity.split(', ')[0]
            street2 = ''
            if len(vicinity.split(', ')) > 1:
                street2 = vicinity.split(', ')[1]
            suburb = self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['locality_verbose']
            self.placerecord = Places(placename=place_name, zomatoplaceid = self.get_zomatoplaceid(), vicinity=vicinity, street1=street1, street2=street2,
                suburb=suburb, postcode=post_code, phonenumber=phone_number)
            db_session.add(self.placerecord)
            db_session.commit()
            self.placeid = self.placerecord.id
        else:
            self.placeid = placeid
        if self.placerecord is None:
            return
        self.placerecord.zomatoplaceid = self.get_zomatoplaceid()
        self.zomatoplacerecord.placeid = self.placeid
        db_session.commit()

    def set_keywords(self):
        if (self.myjson is not None) and (len(self.myjson) > 0):
            zomatoplace_id=self.myjson['pages']['current']['resId']
            datadict = self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_DETAILS']
            keywords = []
            for cuisine in datadict['CUISINES']['cuisines']:
                keywords.append(cuisine['name'])
            for highlight in datadict['HIGHLIGHTS']['highlights']:
                keywords.append(highlight['text'])
            for keyword in keywords:
                add_type_to_place(self.get_placeid(), keyword)

    def opening_hours_to_db(self):
        if (self.myjson is None) or (len(self.myjson) == 0):
            return
        zomatoplace_id=self.myjson['pages']['current']['resId']
        if len(self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['timing']['customised_timings']) == 0:
            return
        if 'opening_hours' not in self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['timing']['customised_timings']:
            return
        timingdict = self.myjson['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['timing']['customised_timings']['opening_hours']
        daysindex = []
        oh = OpeningHours.query.filter(OpeningHours.placeid == self.get_placeid()).first()
        if oh is None:
            oh = OpeningHours(self.get_placeid())
        for hours in timingdict:
            if hours['timing'] == 'Closed':
                continue
            opening = self.convert_timing(hours['timing'].split('\u2013')[0])
            closing = self.convert_timing(hours['timing'].split('\u2013')[-1])
            daysindex.extend(self.get_index_of_days(hours['days']))
            for day in daysindex:
                if day == 'Mon':
                    oh.mondayopen = opening
                    oh.mondayclose = closing
                if day == 'Tue':
                    oh.tuesdayopen = opening
                    oh.tuesdayclose = closing
                if day == 'Wed':
                    oh.wednesdayopen = opening
                    oh.wednesdayclose = closing
                if day == 'Thu':
                    oh.thursdayopen = opening
                    oh.thursdayclose = closing
                if day == 'Fri':
                    oh.fridayopen = opening
                    oh.fridayclose = closing
                if day == 'Sat':
                    oh.saturdayopen = opening
                    oh.saturdayclose = closing
                if day == 'Sun':
                    oh.sundayopen = opening
                    oh.sundayclose = closing
        db_session.add(oh)
        db_session.commit()

    def convert_timing(self, timingstring):
        timingstring = timingstring.replace(' ', '')
        if search(':', timingstring):
            timingstring = timingstring.replace(':', '')
        else:
            timingstring = timingstring + '00'
        if search('am', timingstring):
            timingstring = timingstring.replace('am','')
        if search('pm', timingstring):
            timingstring = str(int(timingstring.replace('pm','')) + 1200)
        if search('12midnight', timingstring):
            timingstring = '0000'
        if search('12noon', timingstring):
            timingstring = '1200'
        return timingstring    

    def get_index_of_days(self, daysstring):
        days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        output = []
        if ', ' in daysstring:
            for mylist in daysstring.split(', '):
                output.extend(self.get_index_of_days(mylist))
        elif '-' in daysstring:
            first, last = daysstring.split('-')
            output.extend(days[days.index(first):days.index(last) + 1])
        else:
            output.append(days[days.index(daysstring)])
        return output


    def get_place_details(self):
        myurl = url + self.zomatoid[1:]
        my_record = ZomatoPlace.query.filter(ZomatoPlace.website == myurl).first()
        if my_record is not None:
            self.zomatoplacerecord = my_record
            self.placeid = self.zomatoplacerecord.placeid
            self.zomatoplaceid = self.zomatoplacerecord.id
            return
        return data_from_url(myurl)


    def get_business_status(self, datadict):
        if datadict['is_perm_closed']:
            return 0
        if datadict['is_temp_closed']:
            return 2
        return 1

    def get_price_level(self, priceob ):
        pricestring = '$0'
        for mydict in priceob:
            pricestring = mydict['title']
        output = pricestring.split(' ')[0]
        output = output[1:]
        return int(output)
    
    def set_jobnumber(self, jobnumber):
        if self.get_placeid() > 0:
            db_session.add(JobResults(placeid=self.get_placeid(), jobid=jobnumber))
            db_session.commit()

    def get_location(self):
        location = dict(lat = self.zomatoplacerecord.lat,
            lng = self.zomatoplacerecord.lng)
        return location
    
    def get_placename(self):
        self.placerecord = Places.query.filter(Places.id == self.placeid).first()
        return self.placerecord.placename

    def get_pluscode(self):
        mylocation = self.get_location()
        return openlocationcode.encode(mylocation.lat, mylocation.lng)


def main():
    while True:
        jobdict = get_job_list('Z')
        if jobdict['jobsAvailable']:
            for job_number in jobdict['joblist']:
                my_job_record = JobList.query.filter(JobList.id == job_number).first()
                location = {'lat': my_job_record.lat, 'lng': my_job_record.lng}
                my_zomato_search = zomatosearch(location=location, radius=my_job_record.radius, address=my_job_record.address)
                zomato_place_list = my_zomato_search.getplaceidlist(job_number)
                my_job_record.roughcount = my_job_record.roughcount + len(zomato_place_list)
                db_session.commit()
        sleep(600)


if __name__ == "__main__":
    main()
