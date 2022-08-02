import logging
import sys
from json import loads, dumps
from urllib import response
import urllib.request, urllib.parse, urllib.error


api_token = "Bearer bxaCOTJs4GXUIdpGK0_m7dtexSrUPijzTtSwmG6V"
zone_id = "251bf895a8d9730c6ee1b09ae76aa431"
account_id = "4855175d02cb9a019342ce2eb901e1c4"
ip_url = "https://api.ipify.org"
cloudflare_url = "https://api.cloudflare.com/client/v4/"

def json_from_url(url, params, method='GET', data=b''):
    paramsstring = urllib.parse.urlencode(params)
    request = urllib.request.Request(url + paramsstring, method=method, data=data)
    request.add_header("Authorization", api_token)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request)
    if response is None:
        raise(f'No response from {url}')
    json_data = loads(response.read())
    return json_data

def text_from_url(url):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    response = response
    if response is None:
        raise(f'No response from {url}')
    return response.read().decode('UTF-8')


def main():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    mylistofdnsrecords = cloudflare_url + "zones/" + zone_id + "/dns_records"
    params =  {'type' : 'A'}
    try:
        logging.debug('Getting external IP address')
        external_ip = text_from_url(ip_url)
        logging.debug(external_ip)
        logging.debug('Getting DNS records')
        myjson = json_from_url(mylistofdnsrecords + '?', params)
        logging.debug(dumps(myjson))
    except Exception as e:
        logging.warning(e)
        quit()
    if myjson['success']:
        for myresult in myjson['result']:
            if myresult['content'] != external_ip:
                mydnsrecordtochange = mylistofdnsrecords + '/' + myresult['id']
                myparams = {'type': 'A',
                    'name': myresult['name'],
                    'content': external_ip,
                    'ttl': myresult['ttl']}
                try:
                    myreturn = json_from_url(mydnsrecordtochange, '', 'PUT', dumps(myparams).encode('UTF-8'))
                except Exception as e:
                    logging.warning(e)
                if myreturn['success']:
                    logging.info(f'{myresult["name"]} has been updated to {external_ip}')
                else:
                    logging.warning(f'{myresult["name"]} has not been updated.')

if __name__ == '__main__':
    main()

