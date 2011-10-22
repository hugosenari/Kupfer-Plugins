'''
Created on Oct 16, 2011

@author: hugosenari
'''

from mprisutils import *
import unittest
import dbus


class Test(unittest.TestCase):


    def test_mpris_utils(self):
        players = MprisUtils.get_players(MprisPlayer)
        for player in players:
            pass
            #player = MprisPlayer("")
            #player.pause()
            #player.play()
            #player.focus()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_mpris_utils']
    unittest.main()