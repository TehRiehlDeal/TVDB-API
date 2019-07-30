import requests
import sanction
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

class TVDB:

    def __init__(self, apikey=config['CREDENTIALS']['APIKEY']):
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Language': 'en'
        }

        self.config = {}

        self.config['authPayload'] = {
            'apikey': config['CREDENTIALS']['APIKEY'],
            'username': '',
            'userkey': ''
        }

        self.config['apiURL'] = "https://api.thetvdb.com"

        self.config['searchEndpoint'] = "{}/search/series".format(self.config['apiURL'])

        self.config['seriesEndpoint'] = "{}/series/".format(self.config['apiURL'])

        self.config['loginURL'] = "{}/login".format(self.config['apiURL'])

        self.__authorized = False
        
        self.session = requests.Session()

    def authorize(self):
        r = self.session.post(self.config['loginURL'], json=self.config['authPayload'], headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise(error)
        token = r.get('token')
        self.headers['Authorization'] = 'Bearer {}'.format(token)
        self.__authorized = True












    def getShow(self, name):
        pass
    def getEpisodes(self, name):
        pass
    def getEpisodeName(self, name, epNum):
        pass
    def cleanName(self, name):
        newName = name.replace('\\', "")
        newName = newName.replace("/", "")
        newName = newName.replace(":", "")
        newName = newName.replace("*", "")
        newName = newName.replace("?", "")
        newName = newName.replace('"', "")
        newName = newName.replace("<", "")
        newName = newName.replace(">", "")
        newName = newName.replace("|", "")
        return newName
