__kupfer_name__ = _('Kupfer Keyring')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__kupfer_sources__ = ("KeysSource",)
__kupfer_actions__ = ("AddKey", "RemoveKey", "Username")
__description__ = '''Use kupfer index your passwords. Use copy action to copy password'''

from kupfer.plugin_support import PluginSettings
__kupfer_settings__ = PluginSettings(
    {
        "key" : "search",
        "label": "Search",
        "type": str,
        "value": "{}"
    }
)

import keyring
import json
from kupfer.objects import Leaf
from kupfer.objects import Source
from kupfer.objects import Action, TextLeaf

def val_of_first(keys, attr):
    for k in keys:
        if k in attr:
            return attr[k]


def filter_keys(items):
    usr_filter = {}
    try:
        j = __kupfer_settings__['search'].replace("'", '"')
        usr_filter = json.loads(j)
    except:
        pass
    expected = set(usr_filter.items())
    for obj in items:
        items = obj.get_attributes().items()
        if not expected or expected.issubset(items):
            yield obj

def user_name(obj):
    keys = ('username', 'user', 'login', 'email', 'e-mail')
    attr = obj.get_attributes()
    return val_of_first(keys, attr) or u''


def service_name(obj):
    keys = ('service', 'application', 'xdg:schema')
    attr = obj.get_attributes()
    return val_of_first(keys, attr) or u'unknown'


class KeyLeaf(Leaf):
    def __init__(self, obj):
        Leaf.__init__(
            self,
            obj,
            service_name(obj) + ': '  + user_name(obj))
    
    def get_text_representation(self):
        secret = self.object.get_secret()
        return str(secret)
    
    def get_description(self):
        return self.object.get_label()


class KeysSource(Source):
    source_user_reloadable = True
    
    def __init__(self):
        Source.__init__(self, _("Keys"))
        self.resource = None
    
    def get_items(self):
        if self.resource:
            for obj in filter_keys(self.resource.get_all_items()):
                yield KeyLeaf(obj)
    
    def initialize(self):
        k = keyring.get_keyring()
        if hasattr(k, 'get_default_collection'):
            self.resource = k.get_default_collection()
        else:
            self.resource = k.get_preferred_collection()


class AddKey(Action):
    def __init__(self):
        Action.__init__(self, name=_("Add Key"))
    
    def activate(self, leaf, oleaf):
        keyring.set_password(
            "KupferKeyring",
            leaf.get_text_representation(),
            oleaf.get_text_representation())
    
    def item_types(self):
        yield TextLeaf
    
    def object_types(self, for_item=None):
        yield TextLeaf
    
    def requires_object(self):
        return True


class RemoveKey(Action):
    def __init__(self):
        Action.__init__(self, name=_("Remove"))
    
    def activate(self, leaf):
        leaf.object.delete()
    
    def item_types(self):
        yield KeyLeaf


class Username(Action):
    def __init__(self):
        Action.__init__(self, name=_("Username"))
    
    def activate(self, leaf):
        username = user_name(leaf.object)
        return TextLeaf(username)
    
    def item_types(self):
        yield KeyLeaf
    
    def get_description(self):
        return "Get key username as text"
    
    def has_result(self):
        return True
    
    def valid_for_item(self, leaf):
        return user_name(leaf.object)
