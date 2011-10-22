'''
Created on Oct 16, 2011

@author: hugosenari
'''


class MprisInterfaces(object):
    MEDIA_PLAYER = 'org.mpris.MediaPlayer2'
    TRACK_LIST = 'org.mpris.MediaPlayer2.TrackList'
    PLAYLISTS = 'org.mpris.MediaPlayer2.Playlists'
    PLAYER = 'org.mpris.MediaPlayer2.Player'
    PROPERTIES = 'org.freedesktop.DBus.Properties'
    SIGNAL='PropertiesChanged'
    OBJECT_PATH = '/org/mpris/MediaPlayer2'
    