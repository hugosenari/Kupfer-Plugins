__kupfer_name__ = _('Kupfer Kering')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''
Use kupfer index your passwords

Use copy action to copy password
'''

__kupfer_sources__ = ("KeysSource",)
__kupfer_actions__ = ("AddKey", "RemoveKey", "Username")

import keyring

def val_of_first(keys, attr):
    for k in keys:
        if k in attr:
            return attr[k]

def user_name(obj):
    keys = ('username', 'user', 'login', 'email', 'e-mail')
    attr = obj.get_attributes()
    return val_of_first(keys, attr) or u''

def service_name(obj):
    keys = ('service', 'application', 'xdg:schema')
    attr = obj.get_attributes()
    return val_of_first(keys, attr) or u'unknown'

def leaf_name(obj):
    return service_name(obj) + ': '  + user_name(obj)
    
from kupfer.objects import Leaf 
class KeyLeaf(Leaf):
    def __init__(self, obj):
        super(KeyLeaf, self).__init__(obj, leaf_name(obj))
    
    def get_text_representation(self):
        secret = self.object.get_secret()
        return str(secret)
    
    def get_description(self):
        return self.object.get_label()


from kupfer.objects import Source

class KeysSource(Source):
    source_user_reloadable = True

    def __init__(self):
        super(self.__class__, self).__init__(_("Keys"))
        self.resource = None
    
    def get_items(self):
        if self.resource:
            for obj in self.resource.get_all_items():
                yield KeyLeaf(obj)
    
    def initialize(self):
        self.resource = keyring.get_keyring().get_default_collection()


from kupfer.objects import Action, TextLeaf

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
