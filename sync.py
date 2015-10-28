__author__ = 'Owner'
from os import walk
from hashlib import sha1
from subprocess import PIPE, Popen
from ConfigParser import ConfigParser

conf_obj = ConfigParser()
conf_obj.read('a3sync.cfg')
conf = {}
conf['include'] = conf_obj.get('directories', 'include').split('\n')
conf['digest'] = conf_obj.get('last_run', 'digest')
directories = walk('.')
command = [
    'rar',
    'a',
    'upi.rar',
]

for directory in directories:
    # os.walk returns the directory we walked prepended for whatever reason, so just substr it out
    the_dir = directory[0][2:]
    if the_dir in conf['include']:
        print "Will archive", the_dir
        command.append(the_dir)
    elif directory[0] == '.':
        for the_file in directory[2]:
            if the_file == 'upi.rar':
                print "Found old upi.rar.  Deleting it..."
                Popen(['rm', '-f', 'upi.rar'])
                print "Done!"
                break

# I'm so sorry.
print "Creating UPI archive..."
stdout = Popen(command, stdout=PIPE).communicate()
print "Done!"

file_digest = sha1('upi.rar').hexdigest()
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
