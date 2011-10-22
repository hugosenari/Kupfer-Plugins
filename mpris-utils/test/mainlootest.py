

from mprisutils import *
import unittest
import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)

def handler(*args, **keywords):
    print '{\n    args:['
    print  '        '+str(args[0]) + ',\n        {'
    for keyword in args[1]:
        print '            '+keyword + ': ' + str(args[1].get(keyword)) + ','
    print '        },\n        '+ str(args[2])
    print '    ],\n    keywords : {'
    for keyword in keywords:
        print '        ' + keyword + ': ' +str(keywords.get(keyword))
    print '    }\n}\n'

    
def test_watch_signal():
    mloop = gobject.MainLoop()
    print MprisPlayer.get_players()
    for player in MprisPlayer.get_players():
        print player.name()
        MprisUtils.watch_signal(player.get_player(), handler)
    mloop.run()


if __name__ == "__main__":
    test_watch_signal()