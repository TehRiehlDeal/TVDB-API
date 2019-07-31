import requests
import sanction
import configparser
import sqlite3


config = configparser.ConfigParser()
config.read('config.ini')

conn = sqlite3.connect('database.db')

c = conn.cursor()

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
            raise(Exception)
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
            raise(Exception)
        return r
        
    def getEpisodes(self, name):
        pass
    def getEpisodeName(self, name, seasonNum, epNum):
        id = self._getShowID(name)
        return self._getEpisodeName(id, seasonNum, epNum)
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


    def _getShowID(self, name):
        if not self.__authorized:
            self.authorize()
        params = {
            'name': name
        }

        r = self.session.get(self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise(Exception)
        return r['data'][0]['id']

    def _getEpisodeName(self, id, seasonNum, epNum):
        params = {
            'airedSeason': seasonNum,
            'airedEpisode': epNum
        }
        r = self.session.get(self.config['seriesEndpoint'] + "/{}/episodes/query".format(id), params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise(Exception)
        return r['data'][0]['episodeName']
        
