import sys
import requests
from requests import Request
from requests import Session
from requests.auth import HTTPBasicAuth


baseURL = 'https://cmapscloud.ihmc.us/resources/rid='
mime_type = 'application/xml'

# pass folder ID on command line
# for example 1QBMKWB9H-27KN8PB-71T
folderID =  sys.argv[1]

# Get the credentials
username = sys.argv[2]
password = sys.argv[3]


# Load cxl file
f = open('templateMap.cxl')
cxl = f.read()
print 'Here is the cxl text: ' + cxl
#
## Load CSV data
#f = open(sys.argv[4], 'rt')
#data = f.read()

# save cmap with res-meta as part of the cxl according to email titled "Fwd: User trying to use our API for CmapServer" on April 24, 2017
# the Cmap and getting back the token ID which is used in the subsequent commands
command = '/?cmd=save.cmap'
start_url = '%s%s%s' % (baseURL, folderID, command)
post_req = requests.post(start_url, auth=(username, password), allow_redirects=True, data=cxl)
resourceID = post_req.text
print 'Here is the post response: ' + resourceID

command = '/?cmd=write.resource.part'
partname = '&partname=cmap'
mimetype = '&mimetype=xml'
url_suffix = command + partname + mimetype
append_url = baseURL + folderID + url_suffix
print 'Here is the append URL:  ' + append_url
post_req = requests.post(append_url, auth=(username, password), allow_redirects=True, data=cxl)


command = '/?cmd=done.saving.resource'
url_suffix = command
save_url = baseURL + folderID + url_suffix
post_req = requests.post(save_url, auth=(username, password), allow_redirects=True)


#Below code from cmapPost.py commented here bec. unnecessary
## Start the process by telling the service the folder where we want to create
## the Cmap and getting back the token ID which is used in the subsequent commands
#command = '/?cmd=begin.creating.resource'
#start_url = '%s%s%s' % (baseURL, folderID, command)
#start_req = requests.post(start_url, auth=(username, password), allow_redirects=True, data=res_meta)
#resourceID = start_req.text
#print resourceID

## Create the resource, passing the CXL file
#command = '/?cmd=write.resource.part'
#create_url = '%s%s%s&partname=cmap&mimetype=%s' % (baseURL, resourceID, command, mime_type)
#create_req = requests.post(create_url, auth=(username, password), allow_redirects=True, data=data)
#print create_req.text

## Tell the server that we're done with the upload process for this Cmap
#command = '/?cmd=done.saving.resource'
#finish_url = '%s%s%s' % (baseURL, resourceID, command)
#finish_req = requests.post(finish_url, auth=(username, password), allow_redirects=True)
#print finish_req.text
