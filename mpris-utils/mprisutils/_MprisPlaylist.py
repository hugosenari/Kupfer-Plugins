'''
Created on Oct 16, 2011

@author: hugosenari
'''

from _MprisInterfaces import *
import _MprisUtils as MprisUtils



class MprisPlaylist(object):
    PROPERTIES_PLAYLIST_COUNT = 'PlaylistCount'
    PROPERTIES_ORDERINGS = 'Orderings'
    PROPERTIES_ACTIVE_PLAYLIST = 'ActivePlaylist'
    ORDERING_ALPHABETICAL = 'Alphabetical'
    ORDERING_CREATIONDATE = 'CreationDate'
    ORDERING_MODIFIEDDATE = 'ModifiedDate'
    ORDERING_LASTPLAYDATE = 'LastPlayDate'
    ORDERING_USERDEFINED = 'UserDefined'

    def __init__(self, playlst, player):
        self._name = playlst.get('Name')
        self._icon = playlst.get('Icon')
        self._id = playlst.get('Id')
        self._player = player.get_player()
        self.player = player

    def _get_property(self, property, iface=MprisInterfaces.PLAYLISTS):
        return MprisUtils.get_properties(self._player, property, iface)

    def _set_property(self, property, val, iface=MprisInterfaces.PLAYLISTS):
        return MprisUtils.set_properties(self._player, property, val, iface)

    def name(self):
        return self._name

    def icon(self):
        return self._icon

    def id(self):
        return self._id

    def play(self):
        pls = MprisUtils.iface(self._player, MprisInterfaces.PLAYLISTS)
        pls.ActivatePlaylist(self.id())
