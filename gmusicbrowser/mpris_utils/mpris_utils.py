import dbus
import re

#hugosenri gmail com
#minha implementacao para mpris, para criar um plugin para kupfer
#em desenvolvimento ainda :D

class Mpris_Interfaces(object):
    MEDIA_PLAYER = 'org.mpris.MediaPlayer2'
    TRACK_LIST = 'org.mpris.MediaPlayer2.TrackList'
    PLAYLISTS = 'org.mpris.MediaPlayer2.Playlists'
    PLAYER = 'org.mpris.MediaPlayer2.Player'
    PROPERTIES = 'org.freedesktop.DBus.Properties'
    OBJECT_PATH = '/org/mpris/MediaPlayer2'


class Mpris_Utils(object):
    dbus_session = None

    @staticmethod
    def get_session():
        if Mpris_Utils.dbus_session == None:
            Mpris_Utils.dbus_session = dbus.SessionBus.get_session()
        return Mpris_Utils.dbus_session

    @staticmethod
    def get_players():
        """
        Retorna lista de players que estejam rodando atualmente
        """
        return [Mpris_Player(item)
            for item in Mpris_Utils.get_session().list_names()
                if re.match(Mpris_Interfaces.MEDIA_PLAYER, item) > 0]

    @staticmethod
    def get_properties(obj, prop, interface):
        ret = None
        try:
            properties = dbus.Interface(obj,
                dbus_interface=Mpris_Interfaces.PROPERTIES)
            ret = properties.Get(interface, prop)
        except Exception:
            if not NONE_PROPERTIES:
                raise Exception
        return ret

    @staticmethod
    def set_properties(obj, prop, val, interface):
        properties = dbus.Interface(obj,
            dbus_interface=Mpris_Interfaces.PROPERTIES)
        properties.Set(interface, prop, val)


class Mpris_Player(object):
    PROPERTIES_CAN_QUIT = 'CanQuit'
    PROPERTIES_CAN_RAISE = 'CanRaise'
    PROPERTIES_CAN_GO_NEXT = 'CanGoNext'
    PROPERTIES_CAN_GO_PREVIOUS = 'CanGoPrevious'
    PROPERTIES_CAN_PLAY = 'CanPlay'
    PROPERTIES_CAN_PAUSE = 'CanPause'
    PROPERTIES_CAN_SEEK = 'CanSeek'
    PROPERTIES_CAN_CONTROL = 'CanControl'
    PROPERTIES_HAS_TRACK_LIST = 'HasTrackList'
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
        self.dbus_session = Mpris_Utils.get_session()
        self.player_uri = player_uri
        self._player = self.dbus_session.get_object(
            player_uri, Mpris_Interfaces.OBJECT_PATH)
        self._playlist = None

    def _get_property(self, property, inteface=Mpris_Interfaces.PLAYER):
        return Mpris_Utils.get_properties(self._player, property, inteface)

    def _set_property(self, property, val, inteface=Mpris_Interfaces.PLAYER):
        return Mpris_Utils.set_properties(self._player, property,
                val, inteface)

    def _fetch_active_playlist(self):
        return self._get_property(
            Mpris_Playlist.PROPERTIES_ACTIVE_PLAYLIST,
            Mpris_Interfaces.PLAYLISTS)

    def _fetch_playlists(self):
        return self._player.GetPlaylist(0, MAX_PLAYLIST_SEARCH,
            ORDER_PLAYLIST_SEARCH, REVERSE_PLAYLIST_SEARCH)

    def _fetch_current_track_info(self):
        return self._get_property(Mpris_Player.PROPERTIES_METADATA)

    def playlist(self, playlist=None, on_change=None):
        if playlist != None:
            playlist.play()
        else:
            active_playlist = self._fetch_active_playlist()
            if(active_playlist != None):
                playlist = Mpris_Playlist(active_playlist, self)
        return playlist

    def playlists(self, on_change=None):
        return [Mpris_Playlist(playlist, self)
            for playlist in self._fetch_playlists]

    def tracklist(self, tracklist=None, on_change=None):
        tracklist = Mpris_Tracklist(self)
        if tracklist != None:
            tracklist.tracks(tracklist)
        else:
            tracklist = Mpris_Tracklist(self)
        return tracklist

    def current_track(self, track=None, on_change=None):
        if(track != None):
            self.open(track)
        else:
            track = Mpris_Track(self._fetch_current_track_info(), self)
        return track

    def focus(self, on_change=None):
        self._player.Raise()

    def quit(self, on_change=None):
        self._player.Quit()

    def supported_mine_type(self, on_change=None):
        return self._get_property(
            Mpris_Player.PROPERTIES_SUPPORTED_MINE_TYPES,
            Mpris_Interfaces.MEDIA_PLAYER)

    def supported_uri_schemes(self, on_change=None):
        return self._get_property(
            Mpris_Player.PROPERTIES_SUPPORTED_URI_SCHEMES,
            Mpris_Interfaces.MEDIA_PLAYER)

    def friendly_name(self):
        return self._get_property(
            Mpris_Player.PROPERTIES_IDENTITY,
            Mpris_Interfaces.MEDIA_PLAYER)

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
        return self._get_property(Mpris_Player.PROPERTIES_POSITION)

    def open(self, track):
        self._player.OpenUri(track.uri())

    def repeat(self, status=None):
        if(status != None):
            self._set_property(Mpris_Player.PROPERTIES_LOOPS_TATUS, status)
        else:
            status = self._get_property(Mpris_Player.PROPERTIES_LOOPS_TATUS)
        return status

    def rate(self, val=None):
        if(val != None):
            self._set_property(Mpris_Player.PROPERTIES_RATE, val)
        else:
            val = self._get_property(Mpris_Player.PROPERTIES_RATE)
        return val

    def volume(self, val=None, on_change=None):
        if(val != None):
            self._set_property(Mpris_Player.PROPERTIES_VOLUME, val)
        else:
            val = self._get_property(Mpris_Player.PROPERTIES_VOLUME)
        return val

    def position(self, track=None, pos=None, on_change=None):
        if track == None and pos != None:
            track = self.current_track()
            self._player.SetPosition(track.id(), pos)
        return self._get_property(Mpris_Player.PROPERTIES_POSITION)

    def hasNext(self, on_change=None):
        return self._get_property(Mpris_Player.PROPERTIES_CAN_GO_NEXT)

    def hasPrev(self, on_change=None):
        return self._get_property(Mpris_Player.PROPERTIES_CAN_GO_PREVIOUS)

    def flags(self):
        return {
            Mpris_Player.PROPERTIES_CAN_GO_NEXT: self.
                _get_property(Mpris_Player.PROPERTIES_CAN_GO_NEXT),
            Mpris_Player.PROPERTIES_CAN_GO_PREVIOUS: self.
                _get_property(Mpris_Player.PROPERTIES_CAN_GO_PREVIOUS),
            Mpris_Player.PROPERTIES_CAN_PLAY: self.
                _get_property(Mpris_Player.PROPERTIES_CAN_PLAY),
            Mpris_Player.PROPERTIES_CAN_PAUSE: self.
                _get_property(Mpris_Player.PROPERTIES_CAN_PAUSE),
            Mpris_Player.PROPERTIES_CAN_SEEK: self.
                _get_property(Mpris_Player.PROPERTIES_CAN_SEEK),
            Mpris_Player.PROPERTIES_CAN_CONTROL: self.
                _get_property(Mpris_Player.PROPERTIES_CAN_CONTROL)
        }

    def get_player(self):
        return self._player


class Mpris_Playlist(object):
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

    def _get_property(self, property, iface=Mpris_Interfaces.PLAYLISTS):
        return Mpris_Utils.get_properties(self._player, property, iface)

    def _set_property(self, property, val, iface=Mpris_Interfaces.PLAYLISTS):
        return Mpris_Utils.set_properties(self._player, property, val, iface)

    def name(self):
        return self._name

    def icon(self):
        return self._icon

    def id(self):
        return self._id

    def play(self):
        self.player.playlist(self)


class Mpris_Tracklist(object):
    PROPERTIES_TACKS = 'Tracks'
    PROPERTIES_CAN_EDIT_TRACKS = 'CanEditTracks'

    def __init__(self, player):
        self._player = player.get_player()
        self.player = player

    def _get_property(self, property, iface=Mpris_Interfaces.TRACK_LIST):
        return Mpris_Utils.get_properties(self._player, property, iface)

    def _set_property(self, property, val, iface=Mpris_Interfaces.TRACK_LIST):
        return Mpris_Utils.set_properties(self._player, property, val, iface)

    def add(self, track, after_track=None, on_change=None):
        af_track_s = '' if after_track == None else after_track.id()
        self._player.AddTrack(track.uri(), af_track_s, False)

    def add_and_play(self, track, after_track=None, on_change=None):
        af_track_s = '' if after_track == None else after_track.id()
        self._player.AddTrack(track.uri(), af_track_s, True)

    def remove(self, track=None, on_change=None):
        if track != None:
            self._player.RemoveTrack(track.id())

    def tracks(self, tracks=None):
        current_tracks = [Mpris_Track(track, self.player)
            for track in self._get_property(Mpris_Tracklist.PROPERTIES_TACKS)]
        if(tracks != None):
            tracks = current_tracks
        else:
            [self.add(track_add) for track_add in tracks]
            [self.remove(track_rem) for track_rem in current_tracks]
        return tracks


class Mpris_Track(object):
    INFO_ART_URI = 'mpris:artUrl'
    INFO_TRACKID = 'mpris:trackid'
    INFO_LENGTH = 'mpris:length'
    INFO_ALBUM = 'xesam:album'
    INFO_ALBUM_ARTIST = 'xesam:albumArtist'
    INFO_ARTIST = 'xesam:artist'
    INFO_AS_TEXT = 'xesam:asText'
    INFO_AUDIO_BPM = 'xesam:audioBPM'
    INFO_AUTO_RATING = 'xesam:autoRating'
    INFO_COMMENT = 'xesam:comment'
    INFO_COMPOSER = 'xesam:composer'
    INFO_CONTENT_CREATED = 'xesam:contentCreated '
    INFO_DISC_NUMBER = 'xesam:discNumber'
    INFO_FIRST_USED = 'xesam:firstUsed'
    INFO_GENRE = 'xesam:genre'
    INFO_LAST_USED = 'xesam:lastUsed'
    INFO_LYRICIST = 'xesam:lyricist'
    INFO_TITLE = 'xesam:title'
    INFO_TRACK_NUMBER = 'xesam:trackNumber '
    INFO_URL = 'xesam:url'
    INFO_USE_COUNT = 'xesam:useCount'
    INFO_USER_RATING = 'xesam:userRating '

    def __init__(self, data, player):
        self.data = data
        self._player = player.get_player()
        self.player = player

    def play(self):
        self._player.current_track(self)

    def id(self):
        return self.get_info(Mpris_Track.INFO_TRACKID)

    def uri(self):
        return self.get_info(Mpris_Track.INFO_URL)

    def lenght(self):
        return self.get_info(Mpris_Track.INFO_LENGTH)

    def get_info(self, property):
        return self.data.get(property)

    def get_player(self):
        return self._player


MAX_PLAYLIST_SEARCH = 100
ORDER_PLAYLIST_SEARCH = Mpris_Playlist.ORDERING_ALPHABETICAL
REVERSE_PLAYLIST_SEARCH = False
NONE_PROPERTIES = True

if __name__ == "__main__":
    players = Mpris_Utils.get_players()
    for player in players:
        #player = Mpris_Player("")
        print "#####"
        print 'player.friendly_name()'
        print player.friendly_name()
        print 'player.hasNext()'
        print player.hasNext()
        print 'player.hasPrev()'
        print player.hasPrev()
        print 'player.flags()'
        print player.flags()
        track = player.current_track()
        print 'track.id()'
        print track.id()
        print 'track.lenght()'
        print track.lenght()
        print 'track.uri()'
        print track.uri()
        print 'track.data'
        print track.data
        print "#####"
        print 'track.get_info(Mpris_Track.INFO_ALBUM)'
        print track.get_info(Mpris_Track.INFO_ALBUM)
        print 'track.get_info(Mpris_Track.INFO_ALBUM_ARTIST)'
        print track.get_info(Mpris_Track.INFO_ALBUM_ARTIST)
        print 'track.get_info(Mpris_Track.INFO_ARTIST)'
        print track.get_info(Mpris_Track.INFO_ARTIST)
        print 'track.get_info(Mpris_Track.INFO_LENGTH)'
        print track.get_info(Mpris_Track.INFO_LENGTH)
        print 'track.get_info(Mpris_Track.INFO_URL)'
        print track.get_info(Mpris_Track.INFO_URL)
        print 'track.get_info(Mpris_Track.INFO_TRACKID)'
        print track.get_info(Mpris_Track.INFO_TRACKID)
        print 'track.get_info(Mpris_Track.INFO_USER_RATING)'
        print track.get_info(Mpris_Track.INFO_USER_RATING)
        print 'track.get_info(Mpris_Track.INFO_TRACK_NUMBER)'
        print track.get_info(Mpris_Track.INFO_TRACK_NUMBER)
        print 'track.get_info(Mpris_Track.INFO_USE_COUNT)'
        print track.get_info(Mpris_Track.INFO_USE_COUNT)
        print 'track.get_info(Mpris_Track.INFO_TITLE)'
        print track.get_info(Mpris_Track.INFO_TITLE)
        print 'track.get_info(Mpris_Track.INFO_LYRICIST)'
        print track.get_info(Mpris_Track.INFO_LYRICIST)
        print 'track.get_info(Mpris_Track.INFO_LAST_USED)'
        print track.get_info(Mpris_Track.INFO_LAST_USED)
        print 'track.get_info(Mpris_Track.INFO_GENRE)'
        print track.get_info(Mpris_Track.INFO_GENRE)
        print 'track.get_info(Mpris_Track.INFO_FIRST_USED)'
        print track.get_info(Mpris_Track.INFO_FIRST_USED)
        print 'track.get_info(Mpris_Track.INFO_DISC_NUMBER)'
        print track.get_info(Mpris_Track.INFO_DISC_NUMBER)
        print 'track.get_info(Mpris_Track.INFO_CONTENT_CREATED)'
        print track.get_info(Mpris_Track.INFO_CONTENT_CREATED)
        print 'track.get_info(Mpris_Track.INFO_COMPOSER)'
        print track.get_info(Mpris_Track.INFO_COMPOSER)
        print 'track.get_info(Mpris_Track.INFO_COMMENT)'
        print track.get_info(Mpris_Track.INFO_COMMENT)
        print 'track.get_info(Mpris_Track.INFO_AUTO_RATING)'
        print track.get_info(Mpris_Track.INFO_AUTO_RATING)
        print 'track.get_info(Mpris_Track.INFO_AUDIO_BPM)'
        print track.get_info(Mpris_Track.INFO_AUDIO_BPM)
        print 'track.get_info(Mpris_Track.INFO_AS_TEXT)'
        print track.get_info(Mpris_Track.INFO_AS_TEXT)
        print 'track.get_info(Mpris_Track.INFO_ART_URI)'
        print track.get_info(Mpris_Track.INFO_ART_URI)
        print "#####"
        #player.pause()
        #player.play()
        #player.focus()