'''
Created on Oct 16, 2011

@author: hugosenari
'''
from _MprisInterfaces import *
from _MprisTrack import MprisTrack
import _MprisUtils as MprisUtils


class MprisTracklist(object):
    PROPERTIES_TACKS = 'Tracks'
    PROPERTIES_CAN_EDIT_TRACKS = 'CanEditTracks'

    def __init__(self, player):
        self.player = player

    def _get_property(self, property, iface=DbusInterfaces.TRACK_LIST):
        return MprisUtils.get_properties(self.player, property, iface)

    def _set_property(self, property, val, iface=DbusInterfaces.TRACK_LIST):
        return MprisUtils.set_properties(self.player, property, val, iface)

    def add(self, track, after_track=None, on_change=None):
        af_track_s = '' if after_track == None else after_track.id()
        self.player.bus_object.AddTrack(track.uri(), af_track_s, False)

    def add_and_play(self, track, after_track=None, on_change=None):
        af_track_s = '' if after_track == None else after_track.id()
        self.player.bus_object.AddTrack(track.uri(), af_track_s, True)

    def remove(self, track=None, on_change=None):
        if track != None:
            self.player.bus_object.RemoveTrack(track.id())

    def tracks(self, tracks=None):
        current_tracks = [MprisTrack(track, self.player)
            for track in self._get_property(MprisTracklist.PROPERTIES_TACKS)]
        if(tracks != None):
            tracks = current_tracks
        else:
            [self.add(track_add) for track_add in tracks]
            [self.remove(track_rem) for track_rem in current_tracks]
        return tracks