'''
Created on Nov 16, 2011

@author: hugosenari
'''

__kupfer_name__ = _("mpris2-plugin-plus")
__kupfer_sources__ = ('PlaylistSource',)
__kupfer_actions__ = ('SelectPlaylistAction',)
__description__ = _("More controls for any mpris2 media player\n\n")
__version__ = "0.1.0"
__author__ = "Hugo Ribeiro"

from kupfer import pretty
from kupfer.plugin_support import PluginSettings
from kupfer.objects import Leaf, Source, Action, AppLeaf

from mpris2 import Playlists, SomePlayers
from mpris2.utils import get_players_uri, get_players_id, get_player_id_from_uri
from mpris2.types import Loop_Status, Metadata_Map, Playlist_Ordering


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
    
    def valid_for_item(self, leaf, **kw):
        for player_uri in get_players_uri():
            if leaf.repr_key() in player_uri:
                return self.valid_for_uri(player_uri, **kw)
        return None
        
    def item_types(self):
        yield AppLeaf
        
    def valid_for_uri(self, player_uri, make=None):
        return make(dbus_uri=player_uri) if make else player_uri


class MediaAction(MediaPlayerAction):
    def __init__(self, name):
        super(MediaAction, self).__init__(name)
        
    def valid_for_item(self, leaf, **kw):
        for player_uri in get_players_uri():
            if leaf.mpris_uri in player_uri:
                result = self.valid_for_uri(leaf.mpris_uri, **kw)
                return result
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
    
    def activate(self, leaf):
        if issubclass(type(leaf), PlaylistLeaf):
            playlists = self.valid_for_item(leaf, make=Playlists)
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
        self._version = 2
        default_player = __kupfer_settings__["default_mpris2_player"]
        players_uri = list(get_players_uri('.+' + default_player))
        self.mpris_uri = mpris_uri
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
            try:
                for playlist in self.playlists.GetPlaylists(
                        0, 20, Playlist_Ordering.LAST_PLAY_DATE, False):
                    yield  PlaylistLeaf(playlist, self.mpris_uri)
            except Exception, exc:
                pretty.print_debug(__name__, 'exceptions', exc)

        
    def get_description(self):
        return _("Default player playlists")
    
    def get_icon_name(self):
        return "playlist"