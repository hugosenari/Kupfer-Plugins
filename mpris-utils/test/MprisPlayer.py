'''
Created on Oct 16, 2011

@author: hugosenari
'''
import unittest
from mprisutils import *

class Test(unittest.TestCase):

    def test_infos(self):
        for player in MprisPlayer.get_players():
            #player = MprisPlayer("")
            print player.friendly_name()
            print player.hasNext()
            print player.hasPrev()
            print player.flags()
            print player.playlist()
            print player.playlists()
            print player.tracklist()
            print player.current_track()
            print player.supported_mine_types()
            print player.supported_uri_schemes()
            print player.seek()
            print player.repeat()
            print player.rate()
            print player.volume()
            print player.position()
            print player.get_player()
    
    def test_controls(self):
        for player in MprisPlayer.get_players():
            player.pause()
            player.play()
            player.stop()
            player.play_pause()
            player.focus()
            print player.current_track().id()
            player.next()
            print player.current_track().id()
            player.prev()
            print player.current_track().id()
            player.next()
            print player.current_track().id()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_infos']
    unittest.main()