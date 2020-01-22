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

    def getShow(self, name):
        """ Gets basic info about the show with given 'name'.
        
        Arguments:
            name {String} -- The name of the show you are searching for.
        
        Raises:
            invalidInput -- Raises if a non string is entered for name.
            showNotFound -- Raises if no show was found for the given name/alias.
        
        Returns:
            dict -- Returns a dictionary containg basic data about the show.
        """
        if type(name) is not str:
            raise invalidInput("You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        params = {
            "name": name
        }
        r = self.session.get(self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise showNotFound("Show was not found, please try again")
        return r
        
    def getEpisodes(self, name, accuracy = 0.8):
        """ Gets a list of all the episodes for a given show.
        
        Arguments:
            name {String} -- The name of the show being searched for.
        
        Keyword Arguments:
            accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})
        
        Raises:
            invalidInput -- Raises if a non string is inputed for name.
            invalidShowID -- Raises if a show was not found.
        
        Returns:
            list -- Returns a list of all the episodes for a given show.
        """
        if type(name) is not str:
            raise invalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
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
        """ Gets an episode by its name, based on the show name, season number, and episode number, and
            cleaned of any special characters so it can be used to name files without error.
        
        Arguments:
            name {String} -- The name of the show being searched for.
            seasonNum {integer} -- The season number which the episode is in.
            epNum {integer} -- The episode number in the season.
        
        Keyword Arguments:
            accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})
        
        Raises:
            invalidInput -- Raises if a non string is inputed for name.
            invalidShowID -- Raises if a show was not found.
        
        Returns:
            String -- Returns the name of the episode searched for, cleaned of all special characters.
        """
        if type(name) is not str or type(seasonNum) is not int or type(epNum) is not int or seasonNum < 0 or epNum < 1:
            raise invalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        id = self._getShowID(name,accuracy)
        if id == -1:
            raise invalidShowID
        return self._getEpisodeName(id, seasonNum, epNum)


    def _authorize(self):
        r = self.session.post(
            self.config['loginURL'], json=self.config['authPayload'], headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise invalidCredentials
        token = r.get('token')
        self.headers['Authorization'] = f'Bearer {token}'
        self.__authorized = True

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
        return self._cleanName(r['data'][0]['episodeName'])

    def _cleanName(self, name):
        newName = name.replace('\\', "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "")
        return newName 
