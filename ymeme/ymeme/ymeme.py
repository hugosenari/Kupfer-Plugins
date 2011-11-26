'''
Created on Nov 24, 2011

@author: hugosenari
'''

__kupfer_name__ = _("ymeme")
#__kupfer_sources__ = ('DashBoardSource', 'MeSource', 'FollowersSource', 'HomeSource')
#__kupfer_actions__ = (
#                      'FindPeopleAction', 'FollowAction', 'UnfollowAction', 'GetMyInformation',
#                      'FindPostAction', 'PublishAction', 'DeleteAction',
#                      'RepostAction', 'CommentAction')
__description__ = _("""Yahoo Meme, plugin.
Require:
    pytripodyql, pyoauthgui and my kupfer version""")
__version__ = "0.1"
__author__ = "Hugo Ribeiro"

from kupfer import plugin_support, pretty, utils

from pytripodyql import TriPod
from pyoauthgui import OauthGui

keyring = None

class Oauth (plugin_support.ExtendedSetting, TriPod):
    '''
    User configuration to store OAuth key
    '''
    def __init__(self, obj=None):
        plugin_support.ExtendedSetting.__init__(self)
        AK = "dj0yJmk9aEhseU1WNUdVR3FnJmQ9WVdrOVFWQkdRWGxRTlRZbWNHbzlNakF3TlRrMU1UQTJNZy0tJnM9Y29uc3VtZXJzZWNyZXQmeD01NQ--"
        SK = "2008f81719f8817f9b38362c936d74375d517af2"

        right_leg = None
        front_leg = None
        if obj:
            if hasattr(obj, "right_leg"):
                right_leg = obj.right_leg
            if hasattr(obj, "front_leg"):
                front_leg = obj.front_leg
        TriPod.__init__(self, AK, SK, right_leg=right_leg, front_leg=front_leg)

    def __repr__(self):
        return '<OAuth "%s", %s>' % (self.right_leg,
                                     bool(self.front_leg))
    
    @classmethod
    def label(cls):
        return _("Get authorization")

    def load(self, plugin_id, key, config_value):
        ''' load @front_leg - from keyring with right_leg (config_value)
        and set user_leg (aka right_leg) as config_value '''
        self.password = keyring.get_password(plugin_id, config_value)
        self.user_leg = config_value

    def save(self, plugin_id, key):
        ''' save @front_leg - store password in keyring and return right_leg
        to save in standard configuration file '''
        keyring.set_password(plugin_id, self.right_leg, self.front_leg)
        return self.right_leg
    
    def ask_config_value(self, plugin_id, key, config_value):
        def callback(code):
            pretty.print_debug(__name__, 'OAuth defined: ', code)
            self.user_leg = code #change it to right_leg to get front_leg
        OauthGui(self.yuri, callback)

## check_keyring_support
try:
    plugin_support.check_keyring_support()
except ImportError:
    global Oauth
    class Oauth (object): pass
    raise

__kupfer_settings__ = plugin_support.PluginSettings(
    {
        'key': 'userpass',
        'label': 'Get authorization',
        'type': Oauth,
        'value': '',
    },
)