'''
Created on Nov 16, 2011

@author: hugosenari
'''
from apt import package
from kupfer.obj.objects import TextLeaf

__kupfer_name__ = _("mpris2-plugin-plus")
__kupfer_sources__ = ('PlaylistSource',)
__kupfer_actions__ = ('SelectPlaylistAction',)
__description__ = _("More controls for any mpris2 media player\n\n Default player changes to last media player you use.")
__version__ = "0.1"
__author__ = "Hugo Ribeiro"

from kupfer import utils, pretty
from kupfer.plugin_support import PluginSettings
from kupfer.obj.apps import AppLeafContentMixin
from kupfer.obj.grouping import ToplevelGroupingSource
from kupfer.obj.compose import ComposedLeaf
from kupfer.objects import Leaf, Source, Action, RunnableLeaf, SourceLeaf, AppLeaf

from mpris2.utils import get_players_uri, get_players_id, get_player_id_from_uri, SomePlayers
from mpris2 import MediaPlayer2, Player, Playlists
from mpris2.types import Loop_Status, Metadata_Map, Playlist_Ordering

import re

__kupfer_settings__ = PluginSettings( 
    {
        "key" : "default_mpris2_player",
        "label": _("Default player"),
        "type": str,
        "value": "None",
        "alternatives": SomePlayers.get_dict().values()
    }
)
#[player_name.split('.')[-1] for player_name in get_players_uri()]

PLUGIN_PLAYERS = {
#    'appid' : 'mprisid'
#    because both are equals they don't need to be here
#    and because they are listed in SomePlayers
#    'gmusicbrowser' : 'gmusicbrowser'
}

class MediaPlayerAction(Action):
    def __init__(self, name):
        Action.__init__(self, name)
    
    def valid_for_item(self, leaf, *args):
        for player_uri in get_players_uri():
            if leaf.repr_key() in player_uri:
                return self.valid_for_uri(player_uri,  *args)
        return None
        
    def item_types(self):
        yield AppLeaf
        
    def valid_for_uri(self, player_uri, make=None):
        return make(dbus_uri=player_uri) if make else player_uri


class MediaAction(MediaPlayerAction):
    def __init__(self, name):
        super(MediaAction, self).__init__(name)
        
    def valid_for_item(self, leaf, *args):
        for player_uri in get_players_uri():
            if leaf.mpris_uri in player_uri:
                return self.valid_for_uri(leaf.mpris_uri,  *args)
        return None

    def item_types(self):
        yield MediaPlayerLeaf


class SelectPlaylistAction(MediaAction):
    def __init__(self):
        super(SelectPlaylistAction, self).__init__(_("Choose Playlist"))
        
    def get_description(self):
        return _("Play this playlist")
    
    def get_icon_name(self):
        return "media-playback-start"
    
    def ativate(self, leaf):
        if issubclass(type(leaf), PlaylistLeaf):
            playlists = self.valid_for_item(leaf, Playlists)
            if playlists:
                playlists.ActivatePlaylist(leaf.object.Id)
    


class MediaPlayerLeaf(Leaf):
    def __init__(self, obj, name, mpris_uri):
        super(MediaPlayerLeaf, self).__init__(obj, name)
        self.mpris_uri = mpris_uri


class PlaylistLeaf(MediaPlayerLeaf):
    def __init__(self, playlist, mpris_uri):
        super(PlaylistLeaf, self).__init__(playlist, playlist.Name, mpris_uri)

    def get_actions(self):
        yield SelectPlaylistAction
        
    def get_description(self):
        return _("Playlist: ") + self.name
    
    def get_icon_name(self):
        return "playlist"
    
    
class PlaylistSource(Source):
    def __init__(self, mpris_uri=None):
        default_player = __kupfer_settings__["default_mpris2_player"]
        players_uri = get_players_uri('.+' + default_player)
        self.mpris_uri = mpris_uri
        self.version = 0.1
        if len(players_uri) > 0 and not mpris_uri: 
            self.mpris_uri = players_uri[0]
            
        name = get_player_id_from_uri(self.mpris_uri) \
            if self.mpris_uri \
                else "Mpris2 Player Playlist"
        
        self.playlists = Playlists(dbus_uri=self.mpris_uri)\
            if self.mpris_uri\
                else None

        super(PlaylistSource, self).__init__(name + _(' playlist'))

        
    def get_items(self):
        if self.playlists:
            pretty.print_debug(__name__, 'get', self.playlists, self.playlists.GetPlaylists(0, 20, Playlist_Ordering.LAST_PLAY_DATE, False))
            try:
                for playlist in self.playlists.GetPlaylists(0, 20, Playlist_Ordering.LAST_PLAY_DATE, False):
                    yield  PlaylistLeaf(playlist, self.mpris_uri)
            except Exception, exc:
                pretty.print_debug(__name__, 'exceptions', exc)

        
    def get_description(self):
        return _("Return playlists")
    
    def get_icon_name(self):
        return "playlist"