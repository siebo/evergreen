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

# Load CSV data
f = open(sys.argv[4], 'rt')
data = f.read()

# Start the process by telling the service the folder where we want to create
# the Cmap and getting back the token ID which is used in the subsequent commands
command = '/?cmd=begin.creating.resource'
start_url = '%s%s%s' % (baseURL, folderID, command)
start_req = requests.post(start_url, auth=(username, password), allow_redirects=True)
resourceID = start_req.text
print resourceID

# Create the resource, passing the CXL file
command = '/?cmd=begin.creating.resource'
create_url = '%s%s%s&partname=cmap&mimetype=%s' % (baseURL, resourceID, command, mime_type)
create_req = requests.post(create_url, auth=(username, password), allow_redirects=True, data=data)
print create_req.text

# Tell the server that we're done with the upload process for this Cmap
command = '/?cmd=done.saving.resource'
finish_url = '%s%s%s' % (baseURL, resourceID, command)
finish_req = requests.post(finish_url, auth=(username, password), allow_redirects=True)
print finish_req.text
