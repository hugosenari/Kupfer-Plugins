__kupfer_name__ = _("mpris2-plugin")
__kupfer_sources__ = ('Mpris2Source',) # 'PlayersSource')
__kupfer_actions__ = ('PlayPauseAction',
                      'NextAction',
                      'PreviousAction',
                      'RaiseAction',
                      'SeekAction',
                      'ShuffleAction',
                      'InfoAction',
                      'PlayerOpenUriAction',)
__description__ = _("Control any mpris2 media player\n\n Default player changes to last media player you use.")
__version__ = "0.1.0"
__author__ = "Hugo Ribeiro <hugosenari gmail com>"

from kupfer import pretty
from kupfer.plugin_support import PluginSettings
from kupfer.obj.compose import ComposedLeaf
from kupfer.objects import Leaf, Source, Action, AppLeaf

from mpris2 import MediaPlayer2, Player, SomePlayers
from mpris2.utils import get_players_uri
from mpris2.types import Loop_Status, Metadata_Map

__kupfer_settings__ = PluginSettings( 
    {
        "key" : "default_mpris2_player",
        "label": _("Default player"),
        "type": str,
        "value": "None",
        "alternatives": SomePlayers.get_dict().values()
    }
)

PLUGIN_PLAYERS = {
#    'appid' : 'mprisid'
#    because both are equals they don't need to be here
#    and because they are listed in SomePlayers
#    'gmusicbrowser' : 'gmusicbrowser'
}

##LEAF

class MediaPlayerLeaf(Leaf):
    def __init__(self, obj, name, mpris_uri):
        super(MediaPlayerLeaf, self).__init__(obj, name)
        self.mpris_uri = mpris_uri

    def get_icon_name(self):
        return "multimedia-player"
    
    def get_description(self):
        return _(self.mpris_uri)


class MediaLeaf(MediaPlayerLeaf):
    serializable = 1
    def __init__(self, media_metadata, mpris_uri=None):
        '''
        @Metadata_Map: mpris2.types.Metadata_Map 
        '''
        name = media_metadata[Metadata_Map.TITLE]
        super(MediaLeaf, self).__init__(media_metadata, name, mpris_uri)
        self.uri = media_metadata[Metadata_Map.URL]
        
    def get_text_representation(self):
        try:
            return self.object[Metadata_Map.AS_TEXT]
        except:
            return self.object[Metadata_Map.TITLE] + ' - ' + ' - '.join(self.object[Metadata_Map.ARTIST])

    def get_description(self):
        return ' - '.join(self.object[Metadata_Map.ARTIST])

    def repr_key(self):
        return self.uri

    def get_icon_name(self):
        return "audio-x-generic"
##/LEAF


##SOURCE

class PlayersSource(Source):
    def __init__(self):
        super(PlayersSource, self).__init__("MPRIS2 Players")
        
    def get_items(self):
        for mpris_uri in get_players_uri('.+'):
            yield MediaPlayerLeaf(mpris_uri, mpris_uri.split('.')[-1], mpris_uri)

    def provides(self):
        yield MediaPlayerLeaf
        
    def get_description(self):
        return _("List all available players")

    def get_icon_name(self):
        return "multimedia-player"


class Mpris2Source (Source):
    instance = None

    def __init__(self):
        super(Mpris2Source, self).__init__("Media Players History")

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
    

class MediaLeafSource(Source):
    def __init__(self, player, player_uri):
        self.player = player
        self.player_uri = player_uri
        super(MediaLeafSource, self).__init__(_("Media Info"))
        
    def get_items(self):
        self.player
        yield MediaLeaf(self.player.Metadata, self.player_uri)
    
    def provides(self):
        yield MediaLeaf


##/SOURCE


##ACTION
##MEDIA_PLAYER_ACTION

class MediaPlayerAction(Action):
    def __init__(self, name):
        super(MediaPlayerAction, self).__init__(name)
    
    def valid_for_item(self, leaf, *args, **kw):
        if hasattr(leaf, 'mpris_uri'):
            return self.valid_for_uri(leaf.mpris_uri,  *args, **kw)
        
        for player_uri in get_players_uri(".+" + leaf.repr_key()):
            Mpris2Source.add_action(self)
            return self.valid_for_uri(player_uri,  *args, **kw)
        return None
        
    def item_types(self):
        yield AppLeaf
        yield MediaPlayerLeaf
    
    def activate(self, leaf):
        Mpris2Source.set_appleaf_instance(leaf)
        
    def valid_for_uri(self, player_uri, make=None):
        return make(dbus_interface_info={'dbus_uri': player_uri}) if make else player_uri


class PlayPauseAction(MediaPlayerAction):
    def __init__(self):
        super(PlayPauseAction, self).__init__(_("Play/Pause"))
    
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
        super(NextAction, self).__init__(_("Next"))
    
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
        super(PreviousAction, self).__init__(_("Previous"))
    
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
        super(RaiseAction, self).__init__(_("Raise"))
    
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
        super(SeekAction, self).__init__(_("Seek"))
    
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
        super(ShuffleAction, self).__init__(_("Toggle Shuffle"))
    
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
        super(RepeatAction, self).__init__(_("Repeat"))
    
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


class InfoAction(MediaPlayerAction):
    def __init__(self):
        super(InfoAction, self).__init__(_("Now playing..."))
        self.player_uri = None

    def is_factory(self):
        return True

    def get_description(self):
        return _("Return now playing media data")
    
    def get_icon_name(self):
        return "audio-x-generic"
    
    def activate(self, leaf):
        super(InfoAction, self).activate(leaf)
        player = self.valid_for_item(leaf, Player)
        if player:
            for player_uri in get_players_uri(".+" + leaf.repr_key()):
                return MediaLeafSource(player, player_uri)
        
    def valid_for_uri(self, player_uri, make=Player):
        player = make(dbus_interface_info={'dbus_uri': player_uri})
        return player if player and player.CanControl else None


##/MEDIA_PLAYER_ACTION


##MEDIA_ACTION

class MediaAction(Action):
    def __init__(self, name):
        super(MediaAction, self).__init__(name)

    def item_types(self):
        yield MediaLeaf

    def get_player(self, leaf):
        return Player(dbus_interface_info={'dbus_uri': leaf.mpris_uri})


class PlayerOpenUriAction(MediaAction):
    def __init__(self):
        super(PlayerOpenUriAction, self).__init__(_("Open Media"))
        
    def get_description(self):
        return _("Play this media")
    
    def get_icon_name(self):
        return "media-playback-start"
    
    def ativate(self, leaf):
        pretty.print_debug(__name__, 'ativate', leaf)
        player = self.get_player(leaf)
        if player:
            player.OpenUri(leaf.uri)

    def valid_for(self, leaf):
        player = self.get_player(leaf)
        pretty.print_debug(__name__, 'valid for', player and player.CanControl)
        return player if player and player.CanControl else None


##/MEDIA_ACTION
##/ACTION
