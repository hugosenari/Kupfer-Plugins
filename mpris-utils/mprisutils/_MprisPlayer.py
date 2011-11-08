'''
Created on Oct 16, 2011

@author: hugosenari
'''

from _MprisInterfaces import DbusInterfaces
from _MprisPlaylist import MprisPlaylist
from _MprisTrack import MprisTrack
from _MprisTracklist import MprisTracklist
import _MprisUtils as MprisUtils
import dbus


class MprisPlayer(object):
    PROPERTIES_CAN_GO_NEXT = 'CanGoNext'
    PROPERTIES_CAN_GO_PREVIOUS = 'CanGoPrevious'
    PROPERTIES_CAN_PLAY = 'CanPlay'
    PROPERTIES_CAN_PAUSE = 'CanPause'
    PROPERTIES_CAN_SEEK = 'CanSeek'
    PROPERTIES_CAN_CONTROL = 'CanControl'
    PROPERTIES_IDENTITY = 'Identity'
    PROPERTIES_DESKTOP_ENTRY = 'DesktopEntry'
    PROPERTIES_SUPPORTED_URI_SCHEMES = 'SupportedUriSchemes'
    PROPERTIES_SUPPORTED_MINE_TYPES = 'SupportedMimeTypes'
    PROPERTIES_PLAYBACK_STATUS = 'PlaybackStatus'
    PROPERTIES_LOOPS_TATUS = 'LoopStatus'
    PROPERTIES_RATE = 'Rate'
    PROPERTIES_SHUFFLE = 'Shuffle'
    PROPERTIES_METADATA = 'Metadata'
    PROPERTIES_VOLUME = 'Volume'
    PROPERTIES_POSITION = 'Position'

    def __init__(self, player_uri):
        self.dbus_session = dbus.SessionBus.get_session()
        self.player_uri = player_uri
        self._player = self.dbus_session.get_object(player_uri,
                                                    DbusInterfaces.OBJECT_PATH)
        self._playlist = None
        self._calbacks = {}

    def _get_property(self, property, inteface=DbusInterfaces.PLAYER):
        try:
            return MprisUtils.get_properties(self._player, property, inteface)
        except Exception:
            if not HIDE_DBUS_ERRORS_AND_RETURN_NONE:
                raise Exception
        return None

    def _set_property(self, property, val, inteface=DbusInterfaces.PLAYER):
        try:
            return MprisUtils.set_properties(self._player, property,
                                             val, inteface)
        except Exception:
            if not HIDE_DBUS_ERRORS_AND_RETURN_NONE:
                raise Exception
        return None


    def _fetch_active_playlist(self):
        try:
            return self._get_property(
                                      MprisPlaylist.PROPERTIES_ACTIVE_PLAYLIST,
                                      DbusInterfaces.PLAYLISTS)
        except Exception:
            if not HIDE_DBUS_ERRORS_AND_RETURN_NONE:
                raise Exception
        return None

    def _fetch_playlists(self):
        try:
            return self._player.GetPlaylist(0, MAX_PLAYLIST_SEARCH,
                                            ORDER_PLAYLIST_SEARCH, REVERSE_PLAYLIST_SEARCH)
        except Exception:
            if not HIDE_DBUS_ERRORS_AND_RETURN_NONE:
                raise Exception
        return []

    def _fetch_current_track_info(self):
        try:
            return self._get_property(MprisPlayer.PROPERTIES_METADATA)
        except Exception:
            if not HIDE_DBUS_ERRORS_AND_RETURN_NONE:
                raise Exception
        return None
    
    def _watch_signal(self, *args, **keywords):
        pass
    
    @staticmethod
    def get_players(pattern=None):
        '''
            Short hand to MprisUtils.get_player(MprisPlayer, pattern)
            return arraMprisPlayer 
        '''
        #try:
        return MprisUtils.get_players(MprisPlayer, pattern)
        #except Exception:
         #   if not HIDE_DBUS_ERRORS_AND_RETURN_NONE:
          #      raise Exception
        #return []

    def playlist(self, playlist=None, on_change=None):
        if playlist != None:
            playlist.play()
        else:
            active_playlist = self._fetch_active_playlist()
            if(active_playlist != None):
                playlist = MprisPlaylist(active_playlist, self)
        self._watch_signal(MprisPlaylist.PROPERTIES_ACTIVE_PLAYLIST, on_change)
        return playlist

    def playlists(self, on_change=None):
        return [MprisPlaylist(playlist, self)
            for playlist in self._fetch_playlists()]

    def tracklist(self, tracklist=None, on_change=None):
        if tracklist != None:
            tracklist.tracks(tracklist)
        else:
            tracklist = MprisTracklist(self)
        return tracklist

    def current_track(self, track=None, on_change=None):
        if(track != None):
            self.open(track)
        else:
            track = MprisTrack(self._fetch_current_track_info(), self)
        return track

    def focus(self, on_change=None):
        self._player.Raise()

    def quit(self, on_change=None):
        self._player.Quit()

    def supported_mine_types(self, on_change=None):
        return self._get_property(
            MprisPlayer.PROPERTIES_SUPPORTED_MINE_TYPES,
            DbusInterfaces.MEDIA_PLAYER)

    def supported_uri_schemes(self, on_change=None):
        return self._get_property(
            MprisPlayer.PROPERTIES_SUPPORTED_URI_SCHEMES,
            DbusInterfaces.MEDIA_PLAYER)

    def name(self):
        return self._get_property(
            MprisPlayer.PROPERTIES_IDENTITY,
            DbusInterfaces.MEDIA_PLAYER)

    def next(self, on_change=None):
        self._player.Next()

    def prev(self, on_change=None):
        self._player.Previous()

    def pause(self, on_change=None):
        self._player.Pause()

    def play_pause(self, on_change=None):
        self._player.PlayPause()

    def play(self, on_change=None):
        self._player.Play()

    def stop(self, on_change=None):
        self._player.Stop()

    def seek(self, offset=None):
        if offset != None:
            self._player.Stop(offset)
        return self._get_property(MprisPlayer.PROPERTIES_POSITION)

    def open(self, track):
        self._player.OpenUri(track.uri())

    def repeat(self, status=None):
        if(status != None):
            self._set_property(MprisPlayer.PROPERTIES_LOOPS_TATUS, status)
        else:
            status = self._get_property(MprisPlayer.PROPERTIES_LOOPS_TATUS)
        return status

    def rate(self, val=None):
        if(val != None):
            self._set_property(MprisPlayer.PROPERTIES_RATE, val)
        else:
            val = self._get_property(MprisPlayer.PROPERTIES_RATE)
        return val

    def volume(self, val=None, on_change=None):
        if(val != None):
            self._set_property(MprisPlayer.PROPERTIES_VOLUME, val)
        else:
            val = self._get_property(MprisPlayer.PROPERTIES_VOLUME)
        return val

    def position(self, track=None, pos=None, on_change=None):
        if track == None and pos != None:
            track = self.current_track()
            self._player.SetPosition(track.id(), pos)
        return self._get_property(MprisPlayer.PROPERTIES_POSITION)

    def hasNext(self, on_change=None):
        return self._get_property(MprisPlayer.PROPERTIES_CAN_GO_NEXT)

    def hasPrev(self, on_change=None):
        return self._get_property(MprisPlayer.PROPERTIES_CAN_GO_PREVIOUS)

    def flags(self):
        return {
            MprisPlayer.PROPERTIES_CAN_GO_NEXT: self.
                _get_property(MprisPlayer.PROPERTIES_CAN_GO_NEXT),
            MprisPlayer.PROPERTIES_CAN_GO_PREVIOUS: self.
                _get_property(MprisPlayer.PROPERTIES_CAN_GO_PREVIOUS),
            MprisPlayer.PROPERTIES_CAN_PLAY: self.
                _get_property(MprisPlayer.PROPERTIES_CAN_PLAY),
            MprisPlayer.PROPERTIES_CAN_PAUSE: self.
                _get_property(MprisPlayer.PROPERTIES_CAN_PAUSE),
            MprisPlayer.PROPERTIES_CAN_SEEK: self.
                _get_property(MprisPlayer.PROPERTIES_CAN_SEEK),
            MprisPlayer.PROPERTIES_CAN_CONTROL: self.
                _get_property(MprisPlayer.PROPERTIES_CAN_CONTROL)
        }

    def get_player(self):
        return self._player


HIDE_DBUS_ERRORS_AND_RETURN_NONE = True
MAX_PLAYLIST_SEARCH = 100
ORDER_PLAYLIST_SEARCH = MprisPlaylist.ORDERING_ALPHABETICAL
REVERSE_PLAYLIST_SEARCH = False