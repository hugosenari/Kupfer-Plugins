from gi.repository import GObject as GO
from folks.go import gtype_and_ctype_of as gtype_of
from folks.geeterator import get_iterator
from folks.folks import FolksListener, it_folks_attrs

if __name__ == '__main__':
    m = GO.MainLoop()
    def ready(agg, *args):
        for uid, name, details in tuple(it_folks_attrs(agg)):
            print(name.encode(), ':' , uid)
            for type_name, key, value in details:
                print(' ' * 4, type_name, key, value.encode())
    FolksListener(ready).initialize()
    m.run()