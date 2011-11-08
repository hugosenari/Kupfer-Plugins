
from _MprisPlayer import MprisPlayer
import _MprisUtils as MprisUtils
import dbus

import gobject
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)

def handler(*args, **keywords):
    print 'handler'
    print args
    print keywords

    
def test_watch_signal():
    mloop = gobject.MainLoop()
    for player in MprisPlayer.get_players():
        print player
        #MprisUtils.watch_signal(player.get_player(), handler)
        player.get_player().connect_to_signal('Seeked', handler)
    mloop.run()


if __name__ == "__main__":
    test_watch_signal()