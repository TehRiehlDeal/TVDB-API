import unittest
from tvdbAPI import TVDB

class TestCase(unittest.TestCase):

    def setUp(self):
        self.t = TVDB()

    def tearDown(self):
        self.t.session.close()
    
    def testA(self):
        assert self.t.getShow("Mythbusters") != -1
    
    def testB(self):
        assert self.t.getShow("TESTSDTSDTETSDD") == -1

    def testC(self):
        assert self.t.getShow(-1) == -1

    def testD(self):
        assert self.t.getShow({'test': "test"}) == -1
    
    def testE(self):
        assert self.t.getShow(["a", "b", "c"]) == -1


if __name__ == "__main__":
    unittest.main()
