'''
Created on Nov 6, 2011

@author: hugosenari
'''

__kupfer_name__ = _("mpris2-plugin")
__kupfer_sources__ = ('Mpris2Source',)
__kupfer_actions__ = ('PlayPauseAction',
                      'NextAction',
                      'PreviousAction',
                      'RaiseAction',
                      'SeekAction',
                      'ShuffleAction',
                      'OpenUriAction',)
__description__ = _("Control any mpris2 media player\n\n Default player changes to last media player you use.")
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


class Mpris2Source (Source):
    instance = None
    #appleaf_content_id = __kupfer_settings__["default_mpris2_player"]
    def __init__(self):
        Source.__init__(self, _("Media Players History"))

    @staticmethod
    def get_appleaf_instance():
        return Mpris2Source.instance.appleaf_instance

    @staticmethod
    def set_appleaf_instance(value):
        if Mpris2Source.instance.appleaf_instance != value:
            Mpris2Source.instance.mark_for_update()
            Mpris2Source.instance.appleaf_instance = value

    @staticmethod        
    def add_action(action):
        Mpris2Source.instance.mark_for_update()
        Mpris2Source.instance.actions_available[hash(action)] = action
    
    @staticmethod
    def delete_action(action):
        Mpris2Source.instance.mark_for_update()
        del Mpris2Source.instance.actions_available[hash(action)]

    def initialize(self):
        Mpris2Source.instance = self
        #Mpris2Source.appleaf_content_id = __kupfer_settings__["default_mpris2_player"]
        self.actions_available = {}
        self.appleaf_instance = None
        self.mark_for_update()
        
    def get_items(self):
        _self = Mpris2Source.instance
        if Mpris2Source.get_appleaf_instance:
            for action in _self.actions_available.values():
                yield ComposedLeaf(_self.appleaf_instance, action)

    def provides(self):
        yield ComposedLeaf
        
    def get_description(self):
        return _("History with Media Player Commands")
    
    def get_icon_name(self):
        return "multimedia-player"


class MediaPlayerAction(Action):
    def __init__(self, name):
        Action.__init__(self, name)
    
    def valid_for_item(self, leaf, *args, **kw):
        for player_uri in get_players_uri():
            if leaf.repr_key() in player_uri:
                Mpris2Source.add_action(self)
                return self.valid_for_uri(player_uri,  *args, **kw)
        return None
        
    def item_types(self):
        yield AppLeaf
    
    def activate(self, leaf):
        Mpris2Source.set_appleaf_instance(leaf)
        
    def valid_for_uri(self, player_uri, make=None):
        return make(dbus_interface_info={'dbus_uri': player_uri}) if make else player_uri
        

class PlayPauseAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Play/Pause"))
    
    def get_description(self):
        return _("Play/Pause current song")
    
    def get_icon_name(self):
        return "media-playback-start"
    
    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        player.PlayPause()
        super(PlayPauseAction, self).activate(leaf)
        
    def valid_for_uri(self, player_uri, make=Player):
        player = make(dbus_interface_info={'dbus_uri': player_uri})
        return player if player and player.CanControl else None


class NextAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Next"))
    
    def get_description(self):
        return _("Jump to next track")
    
    def get_icon_name(self):
        return "media-skip-forward"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        player.Next()
        super(NextAction, self).activate(leaf)
        
    def valid_for_uri(self, player_uri, make=Player):
        player = make(dbus_interface_info={'dbus_uri': player_uri})
        return player if player and player.CanGoNext else None


class PreviousAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Previous"))
    
    def get_description(self):
        return _("Jump to previous track")
    
    def get_icon_name(self):
        return "media-skip-backward"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        player.Previous()
        super(PreviousAction, self).activate(leaf)
        
    def valid_for_uri(self, player_uri, make=Player):
        player = make(dbus_interface_info={'dbus_uri': player_uri})
        return player if player and player.CanGoPrevious else None
    

class RaiseAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Raise"))
    
    def get_description(self):
        return _("Raise player")
    
    def get_icon_name(self):
        return "multimedia-player"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, MediaPlayer2)
        player.Raise()
        super(RaiseAction, self).activate(leaf)
        
    def valid_for_uri(self, player_uri, make=MediaPlayer2):
        player = make(dbus_interface_info={'dbus_uri': player_uri})
        return player if player and player.CanRaise else None
    

class SeekAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Seek"))
    
    def get_description(self):
        return _("Seek current song")
    
    def get_icon_name(self):
        return "media-seek-forward"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        player.Seek(1500) 
        super(SeekAction, self).activate(leaf)
        
    def valid_for_uri(self, player_uri, make=Player):
        player = make(dbus_interface_info={'dbus_uri': player_uri})
        return player if player and player.CanSeek else None
            

class ShuffleAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Toggle Shuffle"))
    
    def get_description(self):
        return _("Toggle shuffle on/off")
    
    def get_icon_name(self):
        return "media-playlist-shuffle"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        super(ShuffleAction, self).activate(leaf)
        status = player.Shuffle
        pretty.print_debug(__name__, status)
        player.Shuffle = not status
        
    def valid_for_uri(self, player_uri, make=Player):
        player = make(dbus_interface_info={'dbus_uri': player_uri})
        return player if player and player.CanControl else None


class RepeatAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Repeat"))
    
    def get_description(self):
        return _("Toggle repeat status none/track/playlist")
    
    def get_icon_name(self):
        return "media-seek-forward"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        if player:
            super(RepeatAction, self).activate(leaf)
            status = player.LoopStatus
            if status == Loop_Status.NONE:
                player.LoopStatus = Loop_Status.TRACK
            elif status == Loop_Status.TRACK:
                player.LoopStatus = Loop_Status.PLAYLIST
            else:
                player.LoopStatus = Loop_Status.NONE
        
    def valid_for_uri(self, player_uri, make=Player):
        player = make(dbus_interface_info={'dbus_uri': player_uri})
        return player if player and player.CanControl else None

class MediaPlayerLeaf(Leaf):
    def __init__(self, obj, name, mpris_uri):
        super(MediaPlayerLeaf, self).__init__(obj, name)
        self.mpris_uri = mpris_uri

class MediaAction(MediaPlayerAction):
    def __init__(self, name):
        super(MediaAction, self).__init__(name)
        
    def valid_for_item(self, leaf, *args):
        for player_uri in get_players_uri():
            if leaf.mpris_uri in player_uri:
                Mpris2Source.add_action(self)
                return self.valid_for_uri(leaf.mpris_uri,  *args)
        return None

    def item_types(self):
        yield MediaPlayerLeaf
        yield MediaLeaf

class OpenUriAction(MediaAction):
    def __init__(self):
        super(OpenUriAction, self).__init__(_("Open Media"))
        
    def get_description(self):
        return _("Play this media")
    
    def get_icon_name(self):
        return "media-playback-start"
    
    def ativate(self, leaf):
        if issubclass(type(leaf), MediaLeaf):
            player = self.valid_for_item(leaf, Player)
            if player:
                player.OpenUri(leaf.uri)


class MediaLeaf(MediaPlayerLeaf):
    serializable = 1
    def __init__(self, media_metadata, mpris_uri, name=None):
        '''
        @Metadata_Map: mpris2.types.Metadata_Map 
        '''
        name = name or media_metadata[Metadata_Map.TITLE]
        super(MediaLeaf, self).__init__(self, media_metadata, name, mpris_uri)
        self.uri = media_metadata[Metadata_Map.URL]
        self.player = player

    def repr_key(self):
        return self.uri

    def get_actions(self):
        yield OpenUriAction

    def get_icon_name(self):
        return "audio-x-generic"
    

class MediaLeaf(MediaPlayerLeaf):
    serializable = 1
    def __init__(self, media_metadata, mpris_uri, name=None):
        '''
        @Metadata_Map: mpris2.types.Metadata_Map 
        '''
        name = name or media_metadata[Metadata_Map.TITLE]
        super(MediaLeaf, self).__init__(self, media_metadata, name, mpris_uri)
        self.uri = media_metadata[Metadata_Map.URL]
        self.player = player

    def repr_key(self):
        return self.uri

    def get_actions(self):
        yield OpenUriAction

    def get_icon_name(self):
        return "audio-x-generic"