'''
Created on Oct 16, 2011

@author: hugosenari
'''
from mprisutils import *
import unittest
import dbus
import re

class Test(unittest.TestCase):
    
    def test_MprisTrack(self):
        players = MprisUtils.get_players(MprisPlayer)
        for player in players:
            track = player.current_track()
            print track.id()
            print track.lenght()
            print track.uri()
            print track.data
            print track.get_info(MprisTrack.INFO_ALBUM)
            print track.get_info(MprisTrack.INFO_ALBUM_ARTIST)
            print track.get_info(MprisTrack.INFO_ARTIST)
            print track.get_info(MprisTrack.INFO_LENGTH)
            print track.get_info(MprisTrack.INFO_URL)
            print track.get_info(MprisTrack.INFO_TRACKID)
            print track.get_info(MprisTrack.INFO_USER_RATING)
            print track.get_info(MprisTrack.INFO_TRACK_NUMBER)
            print track.get_info(MprisTrack.INFO_USE_COUNT)
            print track.get_info(MprisTrack.INFO_TITLE)
            print track.get_info(MprisTrack.INFO_LYRICIST)
            print track.get_info(MprisTrack.INFO_LAST_USED)
            print track.get_info(MprisTrack.INFO_GENRE)
            print track.get_info(MprisTrack.INFO_FIRST_USED)
            print track.get_info(MprisTrack.INFO_DISC_NUMBER)
            print track.get_info(MprisTrack.INFO_CONTENT_CREATED)
            print track.get_info(MprisTrack.INFO_COMPOSER)
            print track.get_info(MprisTrack.INFO_COMMENT)
            print track.get_info(MprisTrack.INFO_AUTO_RATING)
            print track.get_info(MprisTrack.INFO_AUDIO_BPM)
            print track.get_info(MprisTrack.INFO_AS_TEXT)
            print track.get_info(MprisTrack.INFO_ART_URI)