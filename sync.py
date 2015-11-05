__author__ = 'Owner'
from os import walk, remove
from hashlib import sha1
from subprocess import PIPE, Popen
from ConfigParser import ConfigParser

conf_obj = ConfigParser()
conf_obj.read('a3sync.cfg')
secret_obj = ConfigParser()
secret_obj.read('a3sync_secret.cfg')
conf = {}
conf['include'] = conf_obj.get('directories', 'include').split('\n')
conf['digest'] = conf_obj.get('last_run', 'digest')
filename = conf_obj.get('config', 'file_name')
conf['api_key'] = secret_obj.get('config', 'api_key')

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
# TODO
# Actually upload the file
link = ''
print "Uploaded! Link:", link
