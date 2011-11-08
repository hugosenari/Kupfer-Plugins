'''
This code is for use in Kupfer plugin but can be useful in other projects.

The idea is easily control with python, player that implement mprisV2.

Example:
>>>from mprisutils import MprisPlayer
>>>players = MprisPlayer.get_players() # only players running and matched pattern are returned
>>>for player in players:
>>>    player.play()
>>>    player.stop()
>>>    track = player.current_track()
>>>    track.id()
>>>    track.get_info(MprisTrack.INFO_ARTIST)

Created on Oct 16, 2011

@author: hugosenari
'''

from _MprisInterfaces import DbusInterfaces
from _MprisPlaylist import MprisPlaylist
from _MprisTrack import MprisTrack
from _MprisTracklist import MprisTracklist
from _MprisPlayer import MprisPlayer
import _MprisUtils as MprisUtils