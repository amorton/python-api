"""Server and login information to use for tests

The unit tests can either connect to a server or use a mock server connection.
When connected to a server they use the entity id's listed below to add, 
update and delete values. They also add, update and delete schema fields.    

For more details see the test_client.py file.
"""

# If True the api tests are run without connecting to the shotgun server 
# (you still need to provide a server_url below). If False the tests will 
# connect to the server and modify data.
mock = True


# Full url to the Shotgun server server
# e.g. http://my-company.shotgunstudio.com
server_url = ""

http_proxy = None #"http://localhost:8000"
# script name as key as listed in admin panel for your server
script_name = ""
api_key = ""
session_uuid = ""

# ID's of entities to work with during connected tests. 
PROJECT_ID = 4
HUMAN_ID = 39
ASSET_ID = 3
VERSION_ID = 1
    