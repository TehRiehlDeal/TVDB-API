import unittest
import sys
sys.path.append("..")
from tvdbAPI import TVDB, ShowNotFound, InvalidInput, InvalidShowID, NoSuchEpisode, NoActorsFound

class TestGetShow(unittest.TestCase):

    def setUp(self):
        self.t = TVDB()

    def tearDown(self):
        self.t.session.close()
    
    # Test to see if its working correctly
    def testA(self):
        assert type(self.t.getShow("Mythbusters")) == dict
    
    # Test to see if showNotFound is raised correctly
    def testB(self):
        #self.failUnlessRaises(showNotFound, self.t.getShow("TETSTSETSTSETT"))
        with self.assertRaises(ShowNotFound):
            self.t.getShow('TESTSETETS')

    # Tests to see if invalidInput is raised correctly
    def testC(self):
        with self.assertRaises(InvalidInput):
            self.t.getShow(-1)

    def testD(self):
        with self.assertRaises(InvalidInput):
            self.t.getShow({'test': "test"})

    def testE(self):
        with self.assertRaises(InvalidInput):
            assert self.t.getShow(["a", "b", "c"])

    # Tests to see if a show can be successfully found based on an alias.
    # In this case the alias is To aru Majutsu no Index, but it is being matched
    # by string likeness.
    def testF(self):
        assert type(self.t.getShow("Toaru Majutsu no Index")) == dict

    # Tests to see if a showID can be successfully found based on an alias.
    # In this case the alias is To aru Majutsu no Index, but it is being matched
    # by string likeness.
    def testG(self):
        assert self.t.getEpisodes("Toaru Majutsu no Index") != -1

class TestGetEpisodes(unittest.TestCase):

    def setUp(self):
        self.t = TVDB()
    
    def tearDown(self):
        self.t.session.close()

    def testA(self):
        assert type(self.t.getEpisodes("Mythbusters")) == list

    def testB(self):
        with self.assertRaises(ShowNotFound):
            self.t.getEpisodes("TETSETTSTTSETT")
    
    def testC(self):
        with self.assertRaises(InvalidInput):
            self.t.getEpisodes(-1)

class TestGetEpisodeName(unittest.TestCase):
    
    def setUp(self):
        self.t = TVDB()
    
    def tearDown(self):
        self.t.session.close()
    
    def testA(self):
        assert type(self.t.getEpisodeName("Mythbusters", 2003, 1)) == str
    
    def testB(self):
        with self.assertRaises(ShowNotFound):
            self.t.getEpisodeName("TESTSETTSETST", 1, 1)

    def testC(self):
        with self.assertRaises(NoSuchEpisode):
            self.t.getEpisodeName("Mythbusters", 1, 1)

    def testD(self):
        with self.assertRaises(InvalidInput):
            self.t.getEpisodeName(-1, 1, 1)

    def testE(self):
        with self.assertRaises(InvalidInput):
            self.t.getEpisodeName("Mythbusters", "1", 1)

    def testF(self):
        with self.assertRaises(InvalidInput):
            self.t.getEpisodeName("Mythbusters", 1, "1")

    def testG(self):
        with self.assertRaises(InvalidInput):
            self.t.getEpisodeName("Mythbusters", -1, 1)

    def testH(self):
        with self.assertRaises(InvalidInput):
            self.t.getEpisodeName("Mythbusters", 1, -1)  

class TestGetActors(unittest.TestCase):

    def setUp(self):
        self.t = TVDB()

    def tearDown(self):
        self.t.session.close()

    def testA(self):
        assert type(self.t.getActors("Mythbusters")) == dict

class TestGetImages(unittest.TestCase):

    def setUp(self):
        self.t = TVDB()

    def tearDown(self):
        self.t.session.close()

    def testA(self):
        assert type(self.t.getImages("Mythbusters")) == list

if __name__ == "__main__":
    unittest.main()
