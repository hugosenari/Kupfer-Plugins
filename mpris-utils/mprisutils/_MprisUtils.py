'''
Functions to work with DBus

Created on Oct 16, 2011

@author: hugosenari
'''

from _MprisInterfaces import *
import dbus
import re

def get_session():
    '''
        @return: dbus.SessionBus.get_session()
    '''
    return dbus.SessionBus.get_session()

def get_players(callback, pattern=None):
    """
        Call callback with playerDBusBusName param for every player found
        Usage get_players(MprisPlayer) or use MprisPlayer.get_players()  
        
        @param callback: callable object for player bus name
        @param pattern=None: string regexp that filter response 
        @return: array of callback(playerDBusBusName) call result
    """
    return [callback(item)
        for item in get_session().list_names()
            if _match_players_uri(item, pattern)]

def get_players_uri(pattern=None):
    """
        Return string of player bus name
        @param pattern=None: string regexo that filter response
        @return: array string of players bus name
    """
    return [item
        for item in get_session().list_names()
            if _match_players_uri(item, pattern)]


def _match_players_uri(name, pattern=None):
    '''
        Filter logic for get_players and get_player_uri
        @param name: string name to test
        @param pattern=None:  string regexp to test
        @return: boolean
    '''
    mpattern = DbusInterfaces.MEDIA_PLAYER
    if pattern == None:
        return re.match(mpattern, name) > 0
    else:
        return re.match(pattern, name) > 0 and re.match(mpattern, name) > 0  


def iface(obj, dbus_interface=DbusInterfaces.PLAYER):
    '''
    Short hand for dbus.Interface(obj, dbus_interface=DbusInterfaces.PLAYER)
    '''
    return dbus.Interface(obj.bus_object, dbus_interface=dbus_interface)

def get_properties(obj, prop, interface):
    '''
    DBus access for properties
    Set NONE_PROPERTIES to False, if you need exceptions
    
    @param obj: object to get property
    @param prop: str property name
    @param interface: str interface of property
    @return: dbus property or None
    '''
    ret = None
    try:
        properties = iface(obj.bus_object,
                                dbus_interface=DbusInterfaces.PROPERTIES)
        ret = properties.Get(interface, prop)
    except Exception:
        if not NONE_PROPERTIES:
            raise Exception
    return ret

def set_properties(obj, prop, val, interface):
    '''
    DBus access for properties
    Set NONE_PROPERTIES to False, if you need exceptions
    
    @param obj: object to set property
    @param prop: str property name
    @param val: value of property
    @param interface: str interface of property
    @return: val or Exception
    '''
    try:
        properties = iface(obj.bus_object,
                                dbus_interface=DbusInterfaces.PROPERTIES)
        properties.Set(interface, prop, val)
    except Exception:
        if not NONE_PROPERTIES:
            raise Exception
        return Exception
    return val

def watch_signal(obj, callback, 
                 signal_name=DbusInterfaces.SIGNAL,
                 interface=DbusInterfaces.PROPERTIES,
                 sender_keyword='sender',
                 destination_keyword='destination',
                 interface_keyword='iface',
                 member_keyword='member',
                 path_keyword='path'):
    '''
        Wait for a singal
        @param obj: object to watch
        @param callback: callable object to call when receive signal
        @param signa_name=DbusInterfaces.SIGNAL: str member name of signal in interface
        @param interface=DbusInterfaces.PROPERTIES: str interface name of signal
        return signal_name or Exception   
    '''
    print obj, callback
    print interface, signal_name

    signal = iface(obj)
    signal.connect_to_signal(signal_name, callback,
                             sender_keyword=sender_keyword, 
                             destination_keyword=destination_keyword, 
                             interface_keyword=interface_keyword, 
                             member_keyword=member_keyword, 
                             path_keyword=path_keyword)
    return signal_name

NONE_PROPERTIES = True

if __name__ == "__main__":
    pass