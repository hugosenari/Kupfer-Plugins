'''
Created on Oct 16, 2011

@author: hugosenari
'''
from mprisutils import *
import unittest
import dbus
import re

class Test(unittest.TestCase):

    def test_get_session(self):
        assert(type(MprisUtils.get_session()) == dbus.SessionBus)

    def test_get_players_uri(self):
        for uri in MprisUtils.get_players_uri():
            assert(re.match(MprisInterfaces.MEDIA_PLAYER, uri))
        for uri in MprisUtils.get_players_uri(".+mpris.+"):
            assert(re.match(MprisInterfaces.MEDIA_PLAYER, uri))
    
    def test_get_players(self):
        for player in MprisUtils.get_players(MprisPlayer):
            assert(player.friendly_name != '')
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetSession']
    unittest.main()