from gi.repository import GObject as GO
from .go import gtype_and_ctype_of as type_of, c_to_py

class _GeeIterator(object):
    def __init__(self, obj, it):
        self.it = it
        self.obj = obj
        self.size = None
        if hasattr(obj, 'get_size'):
            self.size = obj.get_size()

    def __iter__(self):
        it = self.it
        while it and it.has_next():
            it.next()
            yield it
        raise StopIteration    


class GeeListIterator(_GeeIterator):
    def __init__(self, obj):
        _GeeIterator.__init__(self, obj, obj.iterator())
        self.key_type = GO.GType.from_name('gint')
        self.value_type = None
        if hasattr(obj, 'get_element_type'):
            self.value_type = obj.get_element_type()
    
    def __iter__(self):
        i = 0
        for it in _GeeIterator.__iter__(self):
            value = it.get()
            if self.value_type:
                value = c_to_py(value, self.value_type)
            yield i, value
            i +=1


class GeeMapIterator(_GeeIterator):
    def __init__(self, obj):
        _GeeIterator.__init__(self, obj, obj.map_iterator())
        self.value_type = None
        if hasattr(obj, 'get_value_type'):
            self.value_type = obj.get_value_type()
        self.key_type = None
        if hasattr(obj, 'get_key_type'):
            self.key_type = obj.get_key_type()
    
    def __iter__(self):
        for it in _GeeIterator.__iter__(self):
            value = it.get_value()
            key = it.get_key()
            if self.value_type:
                value = c_to_py(value, self.value_type)
            if self.key_type:
                key = c_to_py(key, self.key_type)
            yield key, value


def get_iterator(obj):
    if hasattr(obj, "map_iterator"):
        return GeeMapIterator(obj)
    if hasattr(obj, "iterator"):
        return GeeListIterator(obj)
    return []
