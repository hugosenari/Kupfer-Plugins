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

from mprisutils._MprisInterfaces import MprisInterfaces
from mprisutils._MprisPlayer import MprisPlayer
from mprisutils._MprisPlaylist import MprisPlaylist
from mprisutils._MprisTrack import MprisTrack
from mprisutils._MprisTracklist import MprisTracklist
import _MprisUtils as MprisUtils