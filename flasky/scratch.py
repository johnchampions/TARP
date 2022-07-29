from asyncio import sleep
import urllib.request
import requests
import time

url = "https://cw.champions.tech:666"

while True:
    status_code = urllib.request.urlopen(url).getcode()
    website_is_up = status_code == 200
    print(website_is_up)
    sleep(10)
