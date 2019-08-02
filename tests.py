import unittest
import sys
sys.path.append("..")
from tvdbAPI import TVDB, showNotFound, invalidInput, invalidShowID

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

if __name__ == "__main__":
    unittest.main()
