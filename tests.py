import unittest
import sys
sys.path.append("..")
from tvdbAPI import TVDB, showNotFound, invalidInput, invalidShowID, noSuchEpisode

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
        with self.assertRaises(showNotFound):
            self.t.getShow('TESTSETETS')

    # Tests to see if invalidInput is raised correctly
    def testC(self):
        with self.assertRaises(invalidInput):
            self.t.getShow(-1)

    def testD(self):
        with self.assertRaises(invalidInput):
            self.t.getShow({'test': "test"})

    def testE(self):
        with self.assertRaises(invalidInput):
            assert self.t.getShow(["a", "b", "c"])

class TestGetEpisodes(unittest.TestCase):

    def setUp(self):
        self.t = TVDB()
    
    def tearDown(self):
        self.t.session.close()

    def testA(self):
        assert type(self.t.getEpisodes("Mythbusters")) == list

    def testB(self):
        with self.assertRaises(showNotFound):
            self.t.getEpisodes("TETSETTSTTSETT")
    
    def testC(self):
        with self.assertRaises(invalidInput):
            self.t.getEpisodes(-1)

class TestGetEpisodeName(unittest.TestCase):
    
    def setUp(self):
        self.t = TVDB()
    
    def tearDown(self):
        self.t.session.close()
    
    def testA(self):
        assert type(self.t.getEpisodeName("Mythbusters", 2003, 1)) == str
    
    def testB(self):
        with self.assertRaises(showNotFound):
            self.t.getEpisodeName("TESTSETTSETST", 1, 1)

    def testC(self):
        with self.assertRaises(noSuchEpisode):
            self.t.getEpisodeName("Mythbusters", 1, 1)

    def testD(self):
        with self.assertRaises(invalidInput):
            self.t.getEpisodeName(-1, 1, 1)

    def testE(self):
        with self.assertRaises(invalidInput):
            self.t.getEpisodeName("Mythbusters", "1", 1)

    def testF(self):
        with self.assertRaises(invalidInput):
            self.t.getEpisodeName("Mythbusters", 1, "1")

    def testG(self):
        with self.assertRaises(invalidInput):
            self.t.getEpisodeName("Mythbusters", -1, 1)

    def testH(self):
        with self.assertRaises(invalidInput):
            self.t.getEpisodeName("Mythbusters", 1, -1)    

if __name__ == "__main__":
    unittest.main()
