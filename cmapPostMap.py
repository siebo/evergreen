import sys
import requests
from requests import Request
from requests import Session
from requests.auth import HTTPBasicAuth


baseURL = 'https://cmapscloud.ihmc.us/resources/rid='
mime_type = 'application/xml'

# pass folder ID on command line
# for example 1QQ3Y21KN-1DZH998-8RG
# TODO: check that cmap name does not already exist in folder, if it does exist, ask user if want to overwrite
# if they do, then make sure res-meta of new version contains <dc:source> tag 
# otherwise rename to map with version#, or get name for new map from user

folderID =  sys.argv[1]

# Get the credentials
username = sys.argv[2]
password = sys.argv[3]


# Load cxl file
#f = open('test.cxl')
f = open('Test Concept Map3.cxl')
cxl = f.read()
print 'Here is the cxl text: ' + cxl
#
## Load CSV data
#f = open(sys.argv[4], 'rt')
#data = f.read()

# save cmap with res-meta as part of the cxl according to email titled "Fwd: User trying to use our API for CmapServer" on April 24, 2017
# the Cmap and getting back the last stanza of the <dc:source> token ID which is used in the subsequent commands
# creation of new maps within folders should contain no <dc:source> 
     # tag (map nodes will not show up in new maps if this exists),
# saving over existing cmaps requires <dc:source> in res-meta file of replacement cmap 
     # (map nodes will not show up if <dc:source> DOES NOT exist in in res-meta submission
command = '/?cmd=save.cmap'
start_url = '%s%s%s' % (baseURL, folderID, command)
post_req = requests.post(start_url, auth=(username, password), allow_redirects=True, data=cxl)
resourceID = post_req.text
# howto crawl res-meta response to get just the <dc:source> tag which contains folder hierarchy in ':' separated stanzas
print 'Here is the post response: ' + resourceID

