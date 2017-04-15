import sys
import requests
from urllib2 import Request
from urllib2 import urlopen
from urllib2 import URLError

baseURL = 'https://cmapscloud.ihmc.us/resources/rid='
username = sys.argv[2]
password = sys.argv[3]

# pass CMAP ID on command line
# for example 1QBMKWB9H-27KN8PB-71T
resourceID =  sys.argv[1]

# GET commands: get.resmeta, get.cmap
commandType = '/?cmd=get.cmap'
requestText = baseURL + resourceID + commandType
url = requestText

requests = requests.get(url, auth=(username, password), allow_redirects=True)
print requests.text
