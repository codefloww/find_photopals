import urllib.request, urllib.parse, urllib.error
import twurl
import json
import ssl
from pprint import pprint
# https://apps.twitter.com/
# Create App and get the four strings, put them in hidden.py
def get_friends(user):
    TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    print('')
    if (len(user) >= 1): 
        url = twurl.augment(TWITTER_URL,
                            {'screen_name': user, 'count': '200'})
        print('Retrieving', url)
        connection = urllib.request.urlopen(url, context=ctx)
        data = connection.read().decode()
        data = json.loads(data)
        return data