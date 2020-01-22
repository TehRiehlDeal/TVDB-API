import requests
import sanction
import configparser
from difflib import SequenceMatcher

config = configparser.ConfigParser()
config.read('config.ini')

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

class invalidInput(Error):
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

        self.config['searchEndpoint'] = f"{self.config['apiURL']}/search/series"

        self.config['seriesEndpoint'] = f"{self.config['apiURL']}/series/"

        self.config['loginURL'] = f"{self.config['apiURL']}/login"

        self.__authorized = False
        
        self.session = requests.Session()

    def authorize(self):
        r = self.session.post(self.config['loginURL'], json=self.config['authPayload'], headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise invalidCredentials
        token = r.get('token')
        self.headers['Authorization'] = f'Bearer {token}'
        self.__authorized = True

    def getShow(self, name):
        if type(name) is not str:
            raise invalidInput("You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self.authorize()
        params = {
            "name": name
        }
        r = self.session.get(self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise showNotFound("Show was not found, please try again")
        return r
        
    def getEpisodes(self, name, accuracy = 0.8):
        if type(name) is not str:
            raise invalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self.authorize()
        id = self._getShowID(name, accuracy)
        if id == -1:
            raise invalidShowID("Show was not found, please try again")
        pages = self.session.get(self.config['seriesEndpoint'] + f"{id}/episodes", headers=self.headers).json()['links']['last']
        episodes = []
        for x in range(1,pages+1):
            params = {
                "page": x
            }
            data = self.session.get(self.config['seriesEndpoint'] + f"{id}/episodes", params=params, headers=self.headers).json()['data']
            for episode in data:
                episodes.append(episode)
        return episodes

    def getEpisodeName(self, name, seasonNum, epNum, accuracy = 0.8):
        if type(name) is not str or type(seasonNum) is not int or type(epNum) is not int or seasonNum < 0 or epNum < 1:
            raise invalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self.authorize()
        id = self._getShowID(name,accuracy)
        if id == -1:
            raise invalidShowID
        return self._getEpisodeName(id, seasonNum, epNum)

    def _getShowID(self, name, accuracy):
        params = {
            'name': name
        }
        r = self.session.get(self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise showNotFound
        for show in r['data']:
            if show['seriesName'].lower() == name.lower():
                return show['id']
            for alias in show['aliases']:
                if SequenceMatcher(None, name.lower(), alias.lower()).ratio() >= accuracy:
                    return show['id']
        return -1

    def _getEpisodeName(self, id, seasonNum, epNum):
        params = {
            'airedSeason': seasonNum,
            'airedEpisode': epNum
        }
        r = self.session.get(self.config['seriesEndpoint'] + f"/{id}/episodes/query", params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise noSuchEpisode("No episode could be found. Please check season or episode number and try again.")
        return self.cleanName(r['data'][0]['episodeName'])

    def cleanName(self, name):
        newName = name.replace('\\', "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "")
        return newName
