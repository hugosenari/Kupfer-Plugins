'''
Created on Oct 16, 2011

@author: hugosenari
'''

class MprisTrack(object):
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
    INFO_CONTENT_CREATED = 'xesam:contentCreated'
    INFO_DISC_NUMBER = 'xesam:discNumber'
    INFO_FIRST_USED = 'xesam:firstUsed'
    INFO_GENRE = 'xesam:genre'
    INFO_LAST_USED = 'xesam:lastUsed'
    INFO_LYRICIST = 'xesam:lyricist'
    INFO_TITLE = 'xesam:title'
    INFO_TRACK_NUMBER = 'xesam:trackNumber'
    INFO_URL = 'xesam:url'
    INFO_USE_COUNT = 'xesam:useCount'
    INFO_USER_RATING = 'xesam:userRating'

    def __init__(self, data, player):
        self.data = data
        self.player = player

    def play(self):
        self.player.bus_object.Open(self)

    def id(self):
        return self.get_info(MprisTrack.INFO_TRACKID)

    def uri(self):
        return self.get_info(MprisTrack.INFO_URL)

    def lenght(self):
        return self.get_info(MprisTrack.INFO_LENGTH)

    def get_info(self, property):
        return self.data.get(property)