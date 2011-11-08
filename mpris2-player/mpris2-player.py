'''
Created on Nov 6, 2011

@author: hugosenari
'''
from apt import package

__kupfer_name__ = _("mpris2-plugin")
#__kupfer_sources__ = ()
__kupfer_actions__ = ('PlayPauseAction', 'NextAction', 'PreviousAction', 'RaiseAction', 'SeekAction')
__description__ = _("Control any mpris2 media player")
__version__ = "0.1"
__author__ = "Hugo Ribeiro"

from kupfer import utils, pretty
from kupfer.plugin_support import PluginSettings
from kupfer.obj.apps import AppLeafContentMixin
from kupfer.obj.grouping import ToplevelGroupingSource
from kupfer.objects import Leaf, Source, Action, AppLeaf, RunnableLeaf, SourceLeaf

from mpris2.utils import get_players_uri, SomePlayers
from mpris2 import MediaPlayer2, Player
from mpris2.types import Loop_Status

__kupfer_settings__ = PluginSettings( 
    {
        "key" : "default_player",
        "label": _("Default player"),
        "type": str,
        "value": "None",
        "alternatives": SomePlayers.get_dict().values()
    }
)#[player_name.split('.')[-1] for player_name in get_players_uri()]

class MediaPlayerAction(Action):
    def __init__(self, name):
        Action.__init__(self, name)
    
    def valid_for_item(self, leaf, make=None):
        for player_uri in get_players_uri():
            if leaf.repr_key() in player_uri:
                return make(dbus_uri=player_uri) if make else player_uri
        return None
        
    def item_types(self):
        yield AppLeaf

class PlayPauseAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Play/Pause"))
    
    def get_description(self):
        return _("Play/Pause current song")
    
    def get_icon_name(self):
        return "media-playback-start"
    
    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        if player.CanControl: player.PlayPause()

class NextAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Next"))
    
    def get_description(self):
        return _("Jump to next track")
    
    def get_icon_name(self):
        return "media-skip-forward"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        if player.CanGoNext: player.Next()

class PreviousAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Previous"))
    
    def get_description(self):
        return _("Jump to previous track")
    
    def get_icon_name(self):
        return "media-skip-backward"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        if player.CanGoPrevious: player.Previous()

class RaiseAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Raise"))
    
    def get_description(self):
        return _("Raise player")
    
    def get_icon_name(self):
        return "multimedia-player"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, MediaPlayer2)
        if player.CanRaise: player.Raise() 

class SeekAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Seek"))
    
    def get_description(self):
        return _("Seek current song")
    
    def get_icon_name(self):
        return "media-seek-forward"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        if player.CanSeek: player.Seek(15000) 

class RepeatAction(MediaPlayerAction):
    def __init__(self):
        MediaPlayerAction.__init__(self, _("Repeat"))
    
    def get_description(self):
        return _("Toggle repeat status none/track/playlist")
    
    def get_icon_name(self):
        return "media-seek-forward"

    def activate(self, leaf):
        player = self.valid_for_item(leaf, Player)
        status = player.LoopStatus
        if status == Loop_Status.NONE:
            player.LoopStatus = Loop_Status.TRACK
        elif status == Loop_Status.TRACK:
            player.LoopStatus = Loop_Status.PLAYLIST
        else:
            player.LoopStatus = Loop_Status.NONE

#class SelectNowPlayingAction(MediaPlayerAction):
#    def __init__(self):
#        super(SelectNowPlayingAction, self).__init__(self, _("Now Playing"))
#    
#    def get_description(self):
#        return _("Play/Pause current song")
#    
#    def get_icon_name(self):
#        return "edit-select-all"
#
#class MediaLeaf(Leaf):
#    pass
#    
#class PlayListsAction(MediaPlayerAction):
#    def __init__(self):
#        super(PlayListsAction, self).__init__(self, _("Playlists"))
#    
#    def get_description(self):
#        return _("List playlists in this player")
#    
#    def get_icon_name(self):
#        return "edit-select-all"
#
#class PlaylistLeaf(Leaf):
#    pass
#
#class TrackListAction(MediaPlayerAction):
#    def __init__(self):
#        super(PlayListsAction, self).__init__(self, _("Now playing list"))
#    
#    def get_description(self):
#        return _("List medias in current tracklist")
#    
#    def get_icon_name(self):
#        return "text-x-boo"
#
#class TrackListLeaf(Leaf):
#    pass