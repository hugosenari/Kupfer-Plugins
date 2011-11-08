'''
Created on Oct 16, 2011

@author: hugosenari
'''


class DbusInterfaces(object):
    MEDIA_PLAYER = 'org.mpris.MediaPlayer2'
    TRACK_LIST = 'org.mpris.MediaPlayer2.TrackList'
    PLAYLISTS = 'org.mpris.MediaPlayer2.Playlists'
    PLAYER = 'org.mpris.MediaPlayer2.Player'
    PROPERTIES = 'org.freedesktop.DBus.Properties'
    SIGNAL='PropertiesChanged'
    OBJECT_PATH = '/org/mpris/MediaPlayer2'
    
    def __init__(self, bus_object=None):
        self.bus_object = bus_object