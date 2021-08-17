from flasky import tar_helper
import urllib.request
import urllib.parse
import json
import time


def dataFromURL(fullURL, apikey, url_params):
    """Grabs a file off the internet.
    input: full URL of the file
    output: a string containing the server response, usually a file
    """
    #time.sleep(5)
    params = urllib.parse.urlencode(url_params)
    headers = {"Accept": "application/json",
        "user-key": str(apikey),
        "User-agent": "curl/7.43.0"}
    request = urllib.request.Request(fullURL + params, headers=headers)
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        raise Exception("Unexpected Error: " + fullURL + " : " + e.reason)
    jsonData = json.loads(response.read())
    return jsonData

class ZomatoScrape:
    
    def __init__(self, apikey):
        self.url = "https://developers.zomato.com/api/v2.1/search?"
        self.apikey = apikey
        self.params = dict()
            "bar": "11",
            "cafe": "6",
            "meal_delivery": "1",
            "meal_takeaway": "5",
            "restaurant": "2"
        }


    def getRestarauntListFromLatLong(self, latlongdict, radius, typelist):
        """Gets a list of restaraunts, cafes, meal palaces etc. from a circle of
        radius around a point latlongdict
        input: latlongdict containing lat lng
        input: integer radius
        output: list of restaraunt dictionaries
        """
        Result = []
        
        self.params["radius"] = str(radius)
        self.params["lat"] = str(latlongdict['lat'])
        self.params["lon"] = str(latlongdict['lng'])
        
        #TODO: This needs to become much more robust.
        for foodpalace in typelist:
            if foodpalace == "liquor_store":
                continue
            self.params["category"] = self.keywordlist[foodpalace]

            data = dataFromURL(self.url, self.apikey, self.params)
            if 'error_message' in data:
                raise Exception("getRestarauntListFRomLatLong: error_message: " + data['error_message'])
            myRestarauntList = self.dataToRestarauntList(data)
            if myRestarauntList is not None:
                Result.extend(myRestarauntList)
        return Result
    
    def businessCategoriesBuilder(self, categoriesData):
        output = []
        for category in categoriesData:
            output.append(category["alias"])
        return output

    def iskosher(self,thing):
        if thing is None:
            return False
        if len(thing) == 0:
            return False
        return True

    def vicinityBuilder(self,vicinity):
        output = vicinity["address"] + ", " + vicinity["zipcode"]
        return output

    def dataToRestarauntList(self, data):
        """Converts a json file into a list of restaraunt dictionaries.
        Will search next page recursively.
        input: json string
        output: list of restaraunt dictionaries
        """
        if 'error_message' in data:
            raise Exception("dataToRestarauntList: error_message: " +  data['error_message'])
        if int(data["results_start"]) + int(data["results_shown"]) < 60:
            myResult = self.getRestarantListFromToken(int(data["results_start"]) + int(data["results_shown"]))
        else:
            myResult = []
        if len(data["restaurants"]) > 0 :
            for aresult in data["restaurants"]:
                if not aresult["restaurant"]["user_rating"]:
                    aresult["restaurant"]["user_rating"]["aggregate_rating"] = 0
                    aresult["restaurant"]["user_rating"]["votes"] = 0
                for n in ("aggregate_rating","votes"):
                    if not n in aresult["restaurant"]["user_rating"]:
                        aresult["restaurant"]["user_rating"][n] = 0
                if not "price_range" in aresult["restaurant"]:
                    aresult["restaurant"]["price_range"] = "0"
                vicinity = self.vicinityBuilder(aresult["restaurant"]["location"])
                myRestaraunt = {
                    "id": aresult["restaurant"]["id"],
                    "name": aresult["restaurant"]["name"],
                    "vicinity": vicinity,
                    "price_level": int(aresult["restaurant"]["price_range"]) *25,
                    "rating": int(float(aresult["restaurant"]["user_rating"]["aggregate_rating"]) * 20) ,
                    "total_user_ratings": aresult["restaurant"]["user_rating"]["votes"],
                    "type": ",".join(aresult["restaurant"]["establishment"])
                }
                myResult.append(myRestaraunt)
                restaurantid = self.add_or_update_restaurant(aresult['restaurant'])
                self.add_keywords(restaurantid, aresult['restaurant'])
        return myResult

    def getRestarantListFromToken(self, resultstart):
        """Gets a list of restaraunt from a next page token
        input: string containing token
        output: list of restaraunt dictionaries
        """
        self.params["start"] = str(resultstart)
        myData = dataFromURL(self.url, self.apikey, self.params)
        if 'error_message' in myData:
            raise Exception("getRestarauntListFromToken: error_message: " + myData['error_message'])
        myOutput = self.dataToRestarauntList(myData)
        return myOutput

    def add_or_update_restaurant(self, aresult):
        street1 = aresult['location']['address'].replace(', ' + aresult['location']['locality_verbose'], '')
        restaurantstate = tar_helper.get_state_from_postcode(aresult['location']['zipcode'])
        restaurantid = tar_helper.logrestaurant(aresult['name'], street1, aresult['location']['locality'], aresult['location']['zipcode'], restaurantstate)
        tar_helper.add_keyword_to_restaurant(restaurantid, aresult['name'].split(' '))
        tar_helper.add_keyword_to_restaurant(restaurantid, street1.split(" "))
        tar_helper.add_keyword_to_restaurant(restaurantid, aresult['location']['locality'])
        tar_helper.add_keyword_to_restaurant(restaurantid, aresult['location']['zipcode'])
        tar_helper.add_keyword_to_restaurant(restaurantid, restaurantstate)
        return restaurantid

    def add_keywords(self, restaurantid, aresult):
        if aresult['R']['has_menu_status']['delivery'] == 1:
            tar_helper.add_keyword_to_restaurant(restaurantid, 'delivery')
        if aresult['R']['has_menu_status']['takeaway'] == 1:
            tar_helper.add_keyword_to_restaurant(restaurantid, 'takeaway')
        tar_helper.add_keyword_to_restaurant(restaurantid, aresult['cuisines'].split(', '))
        tar_helper.add_keyword_to_restaurant(restaurantid, aresult['highlights'])
        tar_helper.add_keyword_to_restaurant(restaurantid, aresult['establishment'])
