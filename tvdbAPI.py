import requests
import sanction
import configparser
import sqlite3


config = configparser.ConfigParser()
config.read('config.ini')

conn = sqlite3.connect('database.db')

c = conn.cursor()

#Exceptions
class Error(Exception):
    pass

class invalidCredentials(Error):
    pass

class showNotFound(Error):
    pass

class noSuchEpisode(Error):
    pass

class invalidShowID(Error):
    pass

#Main TVDB object
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
            raise invalidCredentials
        token = r.get('token')
        self.headers['Authorization'] = 'Bearer {}'.format(token)
        self.__authorized = True

    def getShow(self, name):
        if not self.__authorized:
            self.authorize()
        params = {
            "name": name
        }
        r = self.session.get(self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise showNotFound
        return r
        
    def getEpisodes(self, name):
        pass

    def getEpisodeName(self, name, seasonNum, epNum):
        if not self.__authorized:
            self.authorize()
        id = self._getShowID(name)
        if id == -1:
            raise invalidShowID
        return self._getEpisodeName(id, seasonNum, epNum)

    def _getShowID(self, name):
        params = {
            'name': name
        }

        r = self.session.get(self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise showNotFound
        for show in r['data']:
            if show['seriesName'].lower() == name.lower() or name.lower() in (alias.lower() for alias in show['aliases']):
                return show['id']
        return -1

    def _getEpisodeName(self, id, seasonNum, epNum):
        params = {
            'airedSeason': seasonNum,
            'airedEpisode': epNum
        }
        r = self.session.get(self.config['seriesEndpoint'] + "/{}/episodes/query".format(id), params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise noSuchEpisode
        return self.cleanName(r['data'][0]['episodeName'])

    def cleanName(self, name):
        newName = name.replace('\\', "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "")
        return newName
