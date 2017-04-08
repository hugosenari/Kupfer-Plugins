import gi
gi.require_version('Folks', '0.6')
from gi.repository import Folks
from .go import c_to_py
from .geeterator import get_iterator


_CHANGED = 'individuals_changed_detailed'
class FolksListener(object):
    def __init__(self, on_ready=None, on_change=None):
        self.agg = Folks.IndividualAggregator.dup()
        self.on_ready = on_ready
        self.on_change = on_change
    
    def _on_quiescent(self, *args):
        self.on_ready and self.on_ready(self.agg)
        self.on_change and self.agg.connect(_CHANGED, self.on_change)
    
    def initialize(self):
        self.agg.connect('notify::is-quiescent', self._on_quiescent)
        self.agg.prepare()


class FieldDetailsWrapper(object):
    def __init__(self, obj):
        self.field_details = obj
        self.value_type = None
        if hasattr(obj, 'get_value_type'):
            self.value_type = obj.get_value_type()
        self.value = obj.get_value()
        if self.value_type:
            self.value = c_to_py(self.value, self.value_type)


def it_attr(folk, attr):
    attr_func = getattr(folk, 'get_' + attr)
    attr_val = attr_func()
    it = get_iterator(attr_val)
    for k, v in it:
        wrapper_v = FieldDetailsWrapper(v)
        yield attr, k, wrapper_v.value


def it_attrs(folk):
    yield from it_attr(folk, 'urls')
    yield from it_attr(folk, 'phone_numbers')
    yield from it_attr(folk, 'im_addresses')
    yield from it_attr(folk, 'email_addresses')
    yield from it_attr(folk, 'postal_addresses')
    yield from it_attr(folk, 'roles')
    yield from it_attr(folk, 'notes')
    yield from it_attr(folk, 'web_service_addresses')


def it_folks(agg):
    indies = agg.get_individuals()
    it = get_iterator(indies)
    for folk in it:
        yield folk[1]


def it_folks_attrs(agg):
    indies = agg.get_individuals()
    it = get_iterator(indies)
    # print(gtype_of(it.key_type)[0], gtype_of(it.value_type)[0])
    for uid, folk in it:
        attrs = tuple(it_attrs(folk))
        yield uid, folk.get_display_name(), attrs


def it_changes(changes):
    it = get_iterator(changes)
    for old_folk, new_folk in it:
        yield old_folk, new_folk 
