import dbus
import gobject

loop = gobject.MainLoop()

def start():
    loop.run()

def stop():
    loop.stop()