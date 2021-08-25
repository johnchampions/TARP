import urllib3 

from urllib import parse
http = urllib3.PoolManager()

defaultheaders = {
        "Accept": "*/*",
        "User-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
}

def get(path, params = None,**kwargs):
    if params is dict:
        params = '?' + parse.urlencode(params)
        path = path + params
    r = http.request('GET', path)
    return r

