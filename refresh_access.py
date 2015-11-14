import requests
from ConfigParser import ConfigParser

conf_obj = ConfigParser()
conf_obj.read('a3sync_secret.cfg')
# Open the config file so we can write the new access_token
cfgfile = open('a3sync_secret.cfg', 'w')

data = {
    'refresh_token': conf_obj.get('config', 'refresh_token'),
    'client_id': conf_obj.get('config', 'client_id'),
    'client_secret': conf_obj.get('config', 'client_secret'),
    'grant_type': 'refresh_token',
}

reply = requests.post('https://www.googleapis.com/oauth2/v3/token', data=data)

# Generate some mail if something goes wrong so I can look into it
try:
    reply.raise_for_status()
except Exception as e:
    print "Refresh token failed:", e

conf_obj.set('config', 'access_token', reply.json()['access_token'])
# Write the new access token to the file
conf_obj.write(cfgfile)
cfgfile.close()
