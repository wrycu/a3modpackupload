from os import walk, remove
from hashlib import md5
from subprocess import PIPE, Popen
from ConfigParser import ConfigParser
import requests
from data_dict import DataDict

conf_obj = ConfigParser()
conf_obj.read('a3sync.cfg')
secret_obj = ConfigParser()
secret_obj.read('a3sync_secret.cfg')
conf = {}
conf['include'] = conf_obj.get('directories', 'include').split(',')
filename = conf_obj.get('config', 'file_name')
conf['client_secret'] = secret_obj.get('config', 'client_secret')
conf['client_id'] = secret_obj.get('config', 'client_id')
conf['access_token'] = secret_obj.get('config', 'access_token')
conf['file_id'] = secret_obj.get('config', 'file_id')

'''
# Initial setup:
#  1. Create app in Google (https://console.developers.google.com/apis/credentials). Note that you must set "Authorized redirect URIs", but the URI used need not actually return anything. For example, mine just hits my domain and promptly 404s, but it serves to get the access token
#  1.1. Record client ID and client secret in config file
#  2. Navigate here to get the access token (replace my client ID with yours), noting that the resulting page will contain the access token in the redirected URL, e.g. https://leetsaber.com/callback?code=4/2sf34e#$Fdsvcdsk3S8CdSqQ9o1rns#
#       https://accounts.google.com/o/oauth2/auth?client_id=600859841473-3o2savl23qfperh4t79paj8qp8qhpe8k.apps.googleusercontent.com&response_type=code&scope=https://www.googleapis.com/auth/drive&redirect_uri=http://leetsaber.com/callback&access_type=offline
#  2.1. Set the code in the block below ("code")
#  3. Execute this to convert an access_code to an authorization_token and refresh_token, recording both in the config file
data = {
    'code': 'CODE_HERE',
    'client_id': conf['client_id'],
    'client_secret': conf['client_secret'],
    'redirect_uri': 'http://leetsaber.com/callback',  # replace with the callback URI you defined in your app
    'grant_type': 'authorization_code'
}
reply = requests.post('https://www.googleapis.com/oauth2/v3/token', data=data)
print reply.text
print reply.status_code
exit(0)
'''

#  NOTE: All code beyond here is used to actually upload the file
matched = False
directories = walk('.')
command = [
    'rar',
    'a',
    filename,
]

# Walk the current directory to find the files we're supposed to upload
for directory in directories:
    # os.walk returns the directory we walked prepended for whatever reason, so just substr it out
    the_dir = directory[0][2:]
    if the_dir in conf['include']:
        print "Will archive", the_dir
        command.append(the_dir)
        matched = True
    elif directory[0] == '.':
        for the_file in directory[2]:
            if the_file == filename:
                remove(filename)
                break

if not matched:
    print "Found no matching files. Quitting."
    exit(1)

# I'm so sorry.
print "Creating archive... (this might take a while)"
stdout = Popen(command, stdout=PIPE).communicate()
print "Done!"

# Get the digest of the previously uploaded file
reply = requests.get(
    'https://www.googleapis.com/drive/v2/files/{file}?access_token={token}'.format(
        file=conf['file_id'],
        token=conf['access_token'],
    ),
)

reply.raise_for_status()
previous_digest = reply.json()['md5Checksum']

# Generate the digest of the newly generated file and compare to avoid unnecessary work
print "Calculating the digest of the new archive... (this might take a while)"
file_digest = md5(open(filename, 'rb').read()).hexdigest()
if file_digest == previous_digest:
    print "The archive we just created matches the previously uploaded archive.  Quitting."
    exit(2)

# Actually upload the archive
print "Uploading file... (this might take a while)"
reply = requests.put(
    'https://www.googleapis.com/upload/drive/v2/files/{file}?uploadType=multipart&access_token={token}'.format(
        file=conf['file_id'],
        token=conf['access_token'],
    ),
    files={
        'file': open(filename, 'rb'),
        'data': (
            'metadata',
            DataDict(
                title=filename,
            ),
            'application/json; charset=UTF-8'
        )
    },
)

# Check the response for errors and print the URL (even though it shouldn't change)
reply.raise_for_status()
print "Uploaded! You can access the RAR at", reply.json()['webContentLink']
