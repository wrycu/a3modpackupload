__author__ = 'Owner'
from os import walk, remove
from hashlib import sha1
from subprocess import PIPE, Popen
from ConfigParser import ConfigParser
import requests
from data_dict import DataDict

conf_obj = ConfigParser()
conf_obj.read('a3sync.cfg')
secret_obj = ConfigParser()
secret_obj.read('a3sync_secret.cfg')
conf = {}
conf['include'] = conf_obj.get('directories', 'include').split('\\n')
conf['digest'] = conf_obj.get('last_run', 'digest')
filename = conf_obj.get('config', 'file_name')
conf['client_secret'] = secret_obj.get('config', 'client_secret')
conf['client_id'] = secret_obj.get('config', 'client_id')
conf['access_token'] = secret_obj.get('config', 'access_token')
conf['code'] = secret_obj.get('config', 'code')

# Value you get after navigating to
# https://accounts.google.com/o/oauth2/auth?client_id=600859841473-eer6073rtmclngr45bcvjknj9gmvmiqv.apps.googleusercontent.com&response_type=token&scope=https://www.googleapis.com/auth/drive&redirect_uri=http://localhost
# Uncomment to get the access token
# TODO:
# Make this not retarded.
'''
reply = requests.post(
    'https://accounts.google.com/o/oauth2/token',
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    data='code=' + conf['code'] +
         '&redirect_uri=http://localhost'
         '&client_id=' + conf['client_id'] +
         '&client_secret=' + conf['client_secret'] +
         '&grant_type=authorization_code'
)

reply.raise_for_status()
access_token = reply.json()['access_token']
print access_token
exit(0)
'''


directories = walk('.')
command = [
    'rar',
    'a',
    filename,
]

for directory in directories:
    # os.walk returns the directory we walked prepended for whatever reason, so just substr it out
    the_dir = directory[0][2:]
    if the_dir in conf['include']:
        print "Will archive", the_dir
        command.append(the_dir)
    elif directory[0] == '.':
        for the_file in directory[2]:
            if the_file == filename:
                print "Found old", filename, "Deleting it..."
                remove(filename)
                print "Done!"
                break

# I'm so sorry.
print "Creating archive..."
stdout = Popen(command, stdout=PIPE).communicate()
print "Done!"

file_digest = sha1(filename).hexdigest()
if file_digest == conf['digest']:
    print "The archive we just created matches the previously created archive.  Quitting."
    exit(1)

# TODO
# Write the current digest to the config file
print "Uploading file"

# RARed the wrong files on windows.
# TODO:
# RAR the correct files
reply = requests.post(
    'https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart&access_token=' + conf['access_token'],
    files={
        'file': open(filename, 'rb'),
        'data': (
            'metadata',
            DataDict(
                title=filename
            ),
            'application/json; charset=UTF-8'
        )
    },
)

print reply.status_code
print reply.text
