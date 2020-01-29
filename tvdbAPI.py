import requests
import sanction
import configparser
from difflib import SequenceMatcher

config = configparser.ConfigParser()
config.read('Config.ini')

#Exceptions
class Error(Exception):
    pass

class InvalidCredentials(Error):
    pass

class ShowNotFound(Error):
    pass

class NoSuchEpisode(Error):
    pass

class InvalidShowID(Error):
    pass

class InvalidInput(Error):
    pass

class NoActorsFound(Error):
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

        self.config['imageURL'] = "https://thetvdb.com/banners/"

        self.__authorized = False
        
        self.session = requests.Session()

    def getShow(self, name):
        """ Gets basic info about the show with given 'name'.
        
        Arguments:
            name {String} -- The name of the show you are searching for.
        
        Raises:
            InvalidInput: Raises if a non string is entered for name.
            ShowNotFound: Raises if no show was found for the given name/alias.
        
        Returns:
            dict -- Returns a dictionary containg basic data about the show.
        """
        if type(name) is not str:
            raise InvalidInput("You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        params = {
            "name": name
        }
        r = self.session.get(self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise ShowNotFound("Show was not found, please try again")
        return r
        
    def getEpisodes(self, name, accuracy = 0.8):
        """ Gets a list of all the episodes for a given show.
        
        Arguments:
            name {String} -- The name of the show being searched for.
        
        Keyword Arguments:
            accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})
        
        Raises:
            InvalidInput: Raises if a non string is inputed for name.
            InvalidShowID: Raises if a show was not found.
        
        Returns:
            list -- Returns a list of all the episodes for a given show.
        """
        if type(name) is not str:
            raise InvalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        id = self._getShowID(name, accuracy)
        if id == -1:
            raise InvalidShowID("Show was not found, please try again")
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
            InvalidInput: Raises if a non string is inputed for name.
            InvalidShowID: Raises if a show was not found.
        
        Returns:
            String -- Returns the name of the episode searched for, cleaned of all special characters.
        """
        if type(name) is not str or type(seasonNum) is not int or type(epNum) is not int or seasonNum < 0 or epNum < 1:
            raise InvalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        id = self._getShowID(name,accuracy)
        if id == -1:
            raise InvalidShowID
        return self._getEpisodeName(id, seasonNum, epNum)

    def getActors(self, name, accuracy=0.8):
        """Gets a dictionary of all actors for a given show as well as information on them, and returns it to the user.
        
        Arguments:
            name {String} -- The name of the show.
        
        Keyword Arguments:
            accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})
        
        Raises:
            InvalidInput: Raises if a non string is inputed for name.
            InvalidShowID: Raises if a show was not found.
        
        Returns:
            dict -- A dictionary of all actors for the show, as well as information about them.
        """
        if type(name) is not str:
            raise InvalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        id = self._getShowID(name, accuracy)
        if id == -1:
            raise InvalidShowID("Show was not found, please try again")
        return self._getActors(id)

    def getImages(self, showID):
        pass

    def _authorize(self):
        r = self.session.post(
            self.config['loginURL'], json=self.config['authPayload'], headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise InvalidCredentials
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
            raise ShowNotFound
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
            raise NoSuchEpisode("No episode could be found. Please check season or episode number and try again.")
        return self._cleanName(r['data'][0]['episodeName'])

    def _getActors(self, showID):
        r = self.session.get(self.config['seriesEndpoint'] + f"{showID}/actors", headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise NoActorsFound("No actors found for specific show.")
        return r

    def _cleanName(self, name):
        newName = name.replace('\\', "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "")
        return newName 
