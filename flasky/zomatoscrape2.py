from os import replace
from sqlalchemy.sql.operators import op
from re import split
from functools import cache
import selenium
from db2 import db_session
from bs4 import BeautifulSoup
import json
from models import ZomatoPlace, Places, OpeningHours, KeyWords
from urllib import parse
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

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

class zs2:
    
    url = "https://www.zomato.com/"

    def __init__(self):
        self.radius = 0
             
    def nearby_places(self, location, radius, keyword=''):
        params = {
            'radius' : str(radius),
            'latitude' : str(location['lat']),
            'longitude' : str(location['lng']),
        }
        self.radius = radius
        if keyword != '':
            params['term'] = keyword
        center= self.latlongtocenter(location['lat'], location['lng'])
        cityurl =self.search_city_id(center)
        cityid = center['locationDetails']['cityId'] 
        dineoutlinksearch = self.data_from_url(cityurl)
        for item in dineoutlinksearch['pages']['city'][str(cityid)]['sections']['SECTION_QUICK_SEARCH']['items']:
            if item['categoryType'] == 'dineout':
                dineouturl = item['url']
        linklist = self.selenium_get(dineouturl)
        for link in linklist:
            myurl = self.url + link[1:]
            myjson = self.data_from_url(myurl)
            self.send_to_db(myjson)
            print(json.dumps(myjson))
            print('::')
            time.sleep(15)

    def send_to_db(self, datadict):
        zomatoplace_id=datadict['pages']['current']['resId']
        rating = float(datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['rating']['aggregate_rating'])
        user_rating_total = int(datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['rating']['votes'])
        cuisine = datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['cuisine_string']
        website = self.url + datadict['pages']['current']['pageUrl'][1:]
        business_status = self.get_business_status(datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO'])
        price_level = self.get_price_level(datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTUIN_RES_DETAILS']['CFT_DETAILS']['cfts']['title'])
        lat = float(datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['latitude'])
        lng = float(datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['longitude'])
        
        zomplace = ZomatoPlace.query.filter(ZomatoPlace.zomatoplace_id == datadict['pages']['current']['resId']).first()
        if zomplace is None:
            zomplace = ZomatoPlace(
                zomatoplace_id=zomatoplace_id,
                rating=rating,
                user_rating_total=user_rating_total,
                cuisine=cuisine,
                website=website,
                business_status= business_status,
                price_level=price_level,
                lat=lat,
                lng=lng,
            )
            db_session.add(zomplace)
            db_session.commit()
        
        place_name = datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['name']
        phone_number = datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['phoneDetails']['phoneStr']
        post_code = datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['zipcode']
        vicinity = datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['address']
        street1 = split(vicinity, ', ')[0]
        street2 = split(vicinity, ', ')[2]
        suburb = datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_CONTACT']['locality_verbose']
        placerecord = Places.query.filter((Places.placename == place_name) and (Places.phonenumber == phone_number) and (Places.postcode == post_code)).first()
        if placerecord is None:
            placerecord = Places(placename=place_name, zomatoplaceid = zomplace.id, vicinity=vicinity, street1=street1, street2=street2,
                suburb=suburb, postcode=post_code, phonenumber=phone_number)
            db_session.add(placerecord)
            db_session.commit()
        zomplace.placeid = placerecord.id
        db_session.commit
        keywords = self.get_keywords(datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_RES_DETAILS'], placerecord.id)
        self.keywords_to_db(keywords, placerecord.id)
        self.opening_hours_to_db(datadict['pages']['restaurant'][str(zomatoplace_id)]['sections']['SECTION_BASIC_INFO']['timing']['customised_timings']['opening_hours'])

    def keywords_to_db(self, keywords, placeid):
        for keyword in keywords:
            keyword_record = KeyWords.query.filter(KeyWords.placeid == placeid, KeyWords.placetype == keyword).first()
            if keyword_record is None:
                keyword_record = KeyWords(placeid, keyword)
                db_session.add(keyword_record)
        db_session.commit()

    def get_keywords(self, datadict):
        output = []
        for cuisine in datadict['CUISINES']['cuisines']:
            output.append(cuisine['name'])
        for highlight in datadict['HIGHLIGHTS']['highlights']:
            output.append(highlight['text'])
        return output

    def opening_hours_to_db(self, timingdict, placeid):
        daysindex = []
        oh = OpeningHours.query.filter(OpeningHours.placeid == placeid).first()
        if oh is None:
            oh = OpeningHours(placeid)
        for hours in timingdict:
            opening, closing = split(hours['timing'], ' \u2013 ')
            opening = self.convert_timing(opening)
            closing = self.convert_timing(closing)
            daysindex.extend(self.get_index_of_days(hours['days']))
            for day in daysindex:
                if day == 0:
                    oh.mondayopen = opening
                    oh.mondayclose = closing
                if day == 1:
                    oh.tuesdayopen = opening
                    oh.tuesdayclose = closing
                if day == 2:
                    oh.wednesdayopen = opening
                    oh.wednesdayclose = closing
                if day == 3:
                    oh.thursdayopen = opening
                    oh.thursdayclose = closing
                if day == 4:
                    oh.fridayopen = opening
                    oh.fridayclose = closing
                if day == 5:
                    oh.saturdayopen = opening
                    oh.saturdayclose = closing
                if day == 6:
                    oh.sundayopen = opening
                    oh.sundayclose = closing
        db_session.add(oh)
        db_session.commit()

    def get_index_of_days(self, daysstring):
        days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        output = []
        if ', ' in daysstring:
            for mylist in daysstring.split(', '):
                output.extend(self.get_index_of_days(mylist))
        elif '-' in daysstring:
            first, last = daysstring.split('-')
            output.extend(days[days.index(first):days.index(last)])
        else:
            output.append(days.index(daysstring))
        return output

    def convert_timing(self, timingstring):
        if ':' in timingstring:
            timingstring.replace(':', '')
        else:
            timingstring = timingstring + '00'
        if 'am' in timingstring:
            timingstring.replace('am','')
        if 'pm' in timingstring:
            timingstring = str(int(timingstring.replace('pm','')) + 1200)
        return timingstring





    def get_price_level(self, pricestring ):
        output = split(pricestring, ' ')[0][:1]
        return output
        
    def get_business_status(self, datadict):
        if datadict['is_perm_closed']:
            return 0
        if datadict['is_temp_closed']:
            return 2
        return 1

    def selenium_get(self, url):
        driver = webdriver.Chrome('chromedriver.exe')
        driver.set_window_size(1920,1080)
        driver.get(url)
        sort_by_distance = driver.find_element_by_xpath("//*[@id='root']/div[2]/div[6]/div/div/div[2]/div/div/i")
        sort_by_distance.click()
        can_scroll = True
        last_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(3)
        while can_scroll:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                can_scroll = False
            last_height = new_height
        return self.get_cards(driver.page_source)

    def returnintmeters(self,mystring):
        if mystring.split(' ')[1] == 'm':
            return int(mystring.split(' ')[0])
        if mystring.split(' ')[1] == 'km':
            myint = float(mystring.split(' ')[0]) * 1000
            return int(myint)

    def data_from_url(self, path, params=None):
        if params is None:
            response = requests.get(path, headers=headers)
        else:
            response = requests.get(path, params=params, headers=headers)
        return self.get_preload_json(response.text)

    def get_preload_json(self,page_text):
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


    def get_cards(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        s = soup.find_all('div', class_='jumbo-tracker')
        output = []
        for div in s:
            distance = div.find_all("p")[0].text
            link = div.find_all('a')[0]['href']
            if self.returnintmeters(distance) < self.radius:
                output.append(link)
        return output

    def latlongtocenter(self, lat, lng):
        path = f'{self.url}webroutes/location/get?lat={lat}&lon={lng}'
        response = requests.get(path, headers=headers)
        print(response.url)
        output = json.loads(response.text)
        return output

    def search_city_id(self, latlongtocenter):
        #returns suburbs and collections in json
        path = self.url + 'webapi/searchapi.php'
        params = {'city' : latlongtocenter['locationDetails']['cityId'] }
        response = requests.get(path, headers=headers, params=params)
        output = json.loads(response.text)
        return output['results']['locations']['city']['city_data']['urls']['info']


    

if __name__ == "__main__":
    mybob = zs2()
    location = {
        'lat' : -37.8136,
        'lng' : 144.9631
    }
    mybob.nearby_places(location=location, radius=1000)

        



