#!/usr/local/bin/python3


""" This is a Docstring that will eventually contain all the info"""

import logging
#import json
#import urllib.request
#import urllib.parse
#import csv
import configparser
import argparse
#import time
from fuzzywuzzy import process
import googleScrape
import yelpscrape
import zomatoscrape


defaultRadius = "1000"
defaultOutputFileName = "output.csv"
defaultAddress = "32 Windsor Gardens, London"
url = "https://maps.googleapis.com/maps/api"


def removeRepeats(listOfDictionaries):
    """Removes double entries from our list of restaraunts.
    input: list of dictionaries
    output: slightly shorter list of dictionaries."""

    logging.debug("removeRepeats: listOfDictionaries %s", str(len(listOfDictionaries)))
    myResult = []
    myIds = []
    for myDict in listOfDictionaries:
        if not myDict["id"] in myIds:
            myResult.append(myDict)
            myIds.append(myDict["id"])
    logging.debug("removeRepeats: result: %s", str(len(myResult)))
    return myResult

def remove_repeats_across_lists(firstlist, secondlist):
    """Combines lists into one giant list and amalgamates scores and such
    """
    biglistofrestarauntnames = []
    returnlist = []
    for myrecord in firstlist:
        biglistofrestarauntnames.append(myrecord["name"])
    for myrecord in secondlist:
        (highestname, score) = process.extractOne(myrecord["name"], biglistofrestarauntnames)
        if score > 80:
            myindex = biglistofrestarauntnames.index(highestname)
            returnlist.append(smooshrecords(firstlist[myindex], myrecord))
        else:
            returnlist.append(myrecord)
    return returnlist

def smooshrecords(dict1, dict2):
    """Combines two restaraunt records into one.  Averages out price_level
    and rating accross the two dictionaries."""
    returndict = dict1
    pricelevel = int(((dict1['price_level'] * dict1['total_user_ratings']) + (dict2['price_level'] * dict2['total_user_ratings'])) / (dict1['total_user_ratings'] + dict2['total_user_ratings']))
    returndict.update({'price_level': pricelevel})
    rating = int(((dict1['rating'] * dict1['total_user_ratings']) + (dict2['rating'] * dict2['total_user_ratings'])) / (dict1['total_user_ratings'] + dict2['total_user_ratings']))
    returndict.update({'rating': rating})
    userratings = dict1['total_user_ratings'] + dict2['total_user_ratings']
    returndict.update({'total_user_ratings': userratings})
    returndict.update({'type': dict1['type'] + "," + dict2['type']})
    return returndict

def WriteOutputFile(myFileName, myRestarauntList):
    """Writes restaraunt list out as a Comma Separated Value file
    input: string of file name
    input: list of restaraunt dictionaries
    output: written file.  No program output
    """
    logging.debug("WriteOutputFile: %s, myRestarauntList", myFileName)
    try:
        outputFile = open(myFileName, "w", encoding="utf-8")
        outputFile.write("Name, Address, Price Level, Rating, Total reviews, Type\n")
        for n in myRestarauntList:
            outputFile.write(",".join(("\"" + n["name"] + "\"", "\"" + n["vicinity"] + "\"", str(n["price_level"]), str(n["rating"]), str(n["total_user_ratings"]), "\"" + n["type"] + "\""))+"\n")
        outputFile.close()
    except:
        outputFile.close()
        fatalError("WriteOutputFile: Failed" )

def fatalError(errorString):
    logging.error(errorString)
    print(errorString)
    exit()

def main():
    """ The main function.
    Collects variables from the config file, and the command line
    Sets everything else in motion """
    
    #Set up logging
    logging.basicConfig(filename='logfile.log',level=logging.DEBUG, filemode='w')
    
    #Read Config file for default values
    config = configparser.ConfigParser()
    try:
        logging.debug('Reading config.ini')
        config.read('config.ini')
    except:
        logging.warn('Could not read config.ini.  Hoping all values are on the command line.')
    
    # Reads command line arguments and overwrites config.ini values for anything specified
    logging.debug('Reading Command line arguments')
    parser = argparse.ArgumentParser(description="Gets a list of restaraunts from a circle around an address.")
    parser.add_argument('--address', type=str,
        help="Address you want to search around")
    parser.add_argument('--output', type=str, default=config['DEFAULT']['OutputFileName'],
        help="Output file name")
    parser.add_argument('--radius', type=int, default=int(config['DEFAULT']['Radius']),
        help="Radius of circle you want to search.  (max : 5000)")
    parser.add_argument("--apikey", type=str, default=config['DEFAULT']['googlekey'],
        help="Your Google API key for maps integration")
    parser.add_argument("--yelpkey", type=str, default=config['DEFAULT']['YelpKey'],
        help="Your Yelp API key for getting stuff from yelp.")
    parser.add_argument("--zomatokey", type=str, default=config['DEFAULT']['zomatokey'],
        help="Your Zomato API key for getting stuff from yelp.")
    args = parser.parse_args()
    
    # Sanity check for APIkey
    if (args.apikey == "") or (args.apikey is None):
        fatalError("Cannot have a blank API key.")
    apikey = "key=" + args.apikey
    logging.debug("APIKey: %s", apikey)

    myGoogleScrape = googleScrape.Googlescrape(apikey)

    # Sanity check for APIkey
    if (args.yelpkey == "") or (args.yelpkey is None):
        fatalError("Cannot have a blank API key.")
    yelpkey = args.yelpkey
    logging.debug("APIKey: %s", yelpkey)

    myYelpScrape = yelpscrape.YelpScrape(yelpkey)

    # Sanity check for APIkey
    if (args.zomatokey == "") or (args.zomatokey is None):
        fatalError("Cannot have a blank API key.")
    zomatokey = args.zomatokey
    logging.debug("APIKey: %s", zomatokey)

    myZomatoScrape = zomatoscrape.ZomatoScrape(zomatokey)

    #Sanity check for radius
    if args.radius is None:
        logging.warning('Radius missing.  Assuming program default')
        radius = defaultRadius
    else:
        radius = args.radius
    if (int(radius) > 5000) or (int(radius) < 1):
        fatalError('Radius must be between 1 and 5000 meters.  Currently ' + radius)
    logging.debug("Radius: %s", radius)

    #Sanity check for output File Name
    if (args.output == "") or (args.output is None):
        logging.warning("Output File name missing.  Using program default: %s", defaultOutputFileName)
        outputFileName = defaultOutputFileName
    else:
        outputFileName = args.output
    logging.debug("OutputFileName: %s", outputFileName)

    #Sanity check for address
    if (args.address == "") or (args.address is None):
        logging.warning("No address specified.  Using program default: %s", defaultAddress)
        address = defaultAddress
    else: 
        address = args.address
    logging.debug("Address: %s", address)

    #get Latitude/longitude of address

    latlong = myGoogleScrape.streetAddressToLatLong(address)
    
    #get list of Restaraunts in the area and remove repeats.
    RestarauntList = myGoogleScrape.getRestarauntListFromLatLong(latlong,radius,["bar" , "cafe", "liquor_store","meal_delivery","meal_takeaway", "restaurant"])
    yelpRL = myYelpScrape.getRestarauntListFromLatLong(latlong,radius,["bar" , "cafe", "liquor_store","meal_delivery","meal_takeaway", "restaurant"])
    zomatoRL = myZomatoScrape.getRestarauntListFromLatLong(latlong,radius,["bar" , "cafe", "liquor_store","meal_delivery","meal_takeaway", "restaurant"])

    
    
    #yelpRL = removeRepeats(yelpRL)
    #zomatoRL = removeRepeats(zomatoRL)

    RestarauntList = remove_repeats_across_lists(RestarauntList, yelpRL)
    RestarauntList = remove_repeats_across_lists(RestarauntList,zomatoRL)

    RestarauntList = removeRepeats(RestarauntList)

    #Write to file
    WriteOutputFile(outputFileName, RestarauntList)
    
if __name__ == '__main__':
    main()
