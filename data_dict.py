# Ripped straight from the Internet
# http://stackoverflow.com/questions/23594515/python-request-for-google-drive


class DataDict(dict):
    def read(self):
        return str(self)
