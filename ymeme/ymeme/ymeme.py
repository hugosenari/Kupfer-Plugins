'''
Created on Nov 24, 2011

@author: hugosenari
'''

__kupfer_name__ = _("ymeme")
#__kupfer_sources__ = ('DashBoardSource', 'MeSource', 'FollowersSource', 'HomeSource')
__kupfer_actions__ = (
#                      'FindPeopleAction', 'FollowAction', 'UnfollowAction', 'GetMyInformation',
                      'PublishAction',
#                      'FindPostAction', 'DeleteAction',
#                      'RepostAction', 'CommentAction'
)
__description__ = _("""Yahoo Meme, plugin.
Require:
    pytripodyql, pyoauthgui and my kupfer version""")
__version__ = "0.1"
__author__ = "Hugo Ribeiro"

from kupfer import plugin_support, pretty, utils

from pytripodyql import TriPod
from pyoauthgui.pywebkitgtk import OauthGui


import keyring, time

class Oauth (plugin_support.ExtendedSetting):
    '''
    User configuration to store OAuth key
    '''
    def __init__(self, obj=None):
        if plugin_support:
            plugin_support.ExtendedSetting.__init__(self)
        AK = "dj0yJmk9WjNaQkoxdDZyanJ2JmQ9WVdrOVYyTjNkMFJYTm1jbWNHbzlNVE13TWpBd05EVS0mcz1jb25zdW1lcnNlY3JldCZ4PWQ0"
        SK = "9d8c16493dfc5de7010f9cd173e91cb82d63f924"
        self.time = time.time()
        front_leg = None
        if obj:
            if hasattr(obj, "object") and hasattr(obj.object, "front_leg"):
                front_leg = str(obj.object)
        self.object = TriPod(AK, SK, front_leg=front_leg)
        #pretty.print_debug(__name__, 'Config created, verifier:', self.time)
        

    def __repr__(self):
        return '<OAuth "%s", %s>' % (self.object.right_leg,
                                     bool(self.object.token_leg))
    
    @classmethod
    def label(cls):
        return _("Get authorization")

    def load(self, plugin_id, key, config_value):
        ''' load @front_leg - from keyring with right_leg (config_value)
        and set user_leg (aka right_leg) as config_value '''
        token = keyring.get_password(plugin_id, config_value)
        self.object.front_leg = token
        self.object.user_leg = config_value
#        pretty.print_debug(__name__, 'Config loaded:', self.object.token_leg,
#                               ', verifier:', self.time)

    def save(self, plugin_id, key):
        ''' save @front_leg - store password in keyring and return right_leg
        to save in standard configuration file '''
#        pretty.print_debug(__name__, 'Config saved:', self.object.token_leg,
#                               ', verifier:', self.time)
        keyring.set_password(plugin_id, self.object.user_leg, str(self.object))
        return self.object.right_leg
    
    def ask_config_value(self, plugin_id, key, config_value, save_callback):
        def callback(code):
            self.object.right_leg = code
            save_callback()
        OauthGui(self.object.yuri, callback)
    
    def defined(self):
        try:
#            pretty.print_debug(__name__, 'Validating config:', self.object.token_leg,
#                               ', verifier:', self.time,
#                               'valid:', bool(self.object and self.object.token_leg))
            return self.object and self.object.token_leg
        except:
            return False
        

__kupfer_settings__ = plugin_support.PluginSettings(
    {
        'key': 'tripod',
        'label': 'Get authorization',
        'type': Oauth,
        'value': None,
    },
)

from kupfer.objects import Action, TextLeaf
class MemeAction(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.tripod = None
        self.cfg = None
        
    def valid_for_item(self, item):
        if not self.cfg:
            self.cfg = __kupfer_settings__['tripod']

        if self.cfg and self.cfg.defined():
            if not self.tripod:
                self.tripod = self.cfg.object
            return bool(self.tripod)
        return False

    def _execute(self, query):
        return self.tripod.execute(query)

    def get_my_info(self, uid="me"):
        return self._execute("select * from meme.info where owner_guid=%s" % (uid,))

    def post(self, content):
        return self._execute("insert into meme.user.posts (type, content" + content)

    def post_media(self, tpe, content, caption = ""):
        return self.post(", caption) values (\"%s\", \"%s\", \"%s\")" % (tpe, content, caption))

    def post_text(self, *args, **kw):
        return self.post_media("text", *args, **kw)

    def post_video(self, *args, **kw):
        return self.post_media("video", *args, **kw)

    def post_audio(self, *args, **kw):
        return self.post_media("audio", *args, **kw)

    def post_image(self, *args, **kw):
        return self.post_media("photo", *args, **kw)

    def delete(self, pid):
        return self._execute("delete from meme.user.posts where pubid = \"%s\"" % (pid,))

    def follow(self, uid):
        return self._execute("insert into meme.user.following (guid) values (\"%s\")" % (uid,))

    def unfollow(self, uid):
        return self._execute("delete from meme.user.posts where guid = \"%s\"" % (uid,))

    def comment(self, uid, pid, comment):
        return self._execute("insert into meme.user.comments (guid, pubid, comment) values (\"%s\",\"%s\",\"%s\")" % (uid, pid, comment))

    def repost(self, uid, pid, comment):
        return self._execute("insert into meme.user.posts (guid, pubid, comment) values (\"%s\",\"%s\",\"%s\")" % (uid, pid, comment))

    def dash_board(self):
        return self._execute("select * from meme.user.dashboard")

    def syql_execute(self, query, param):
        return self.tripod.execute(query, param)

class PublishAction(MemeAction):
    '''Create new post action'''
    def __init__(self):
        MemeAction.__init__(self, _('New Meme post'))

    def item_types(self):
        yield TextLeaf

    def get_description(self):
        return _("Create new post at Yahoo Meme")

    def activate(self, leaf):
        self.post_text(leaf.object)
        
        
        
        