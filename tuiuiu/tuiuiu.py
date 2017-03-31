__kupfer_name__ = _('Tuiuiu - Twitter')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''Kupfer twitter plugin'''
__kupfer_actions__ = ("UpdateTwitterStatus",)

from kupfer.plugin_support import PluginSettings, OAuth1, check_oauth_support
__kupfer_settings__ = PluginSettings( 
    {
        "key" : "oauth",
        "label": _("Access Token"),
        "type": OAuth1,
        "value": OAuth1(
            plugin_id="j4pXhBEUqF09ND6enp8hLFKcJ",
            plugin_secret="TEw7p7VFdEjqfrOn1etDLj5a2boup4EJw55XxMqlBeSkUgHjSv",
            url_access="https://api.twitter.com/oauth/access_token",
            url_auth="https://api.twitter.com/oauth/authorize",
            url_request="https://api.twitter.com/oauth/request_token",
            url_callback="https://hugosenari.github.io/Kupfer-Plugins/token.html"
        ),
    }
)

check_oauth_support()

from kupfer.objects import Action, TextLeaf
from requests_oauthlib import OAuth1Session
class UpdateTwitterStatus(Action):
    def __init__(self):
        Action.__init__(self, name=_("Update Twitter Status"))

    def activate(self, leaf):
        cfg = __kupfer_settings__["oauth"]
        oauth = OAuth1Session(cfg.plugin_id,
                              client_secret=cfg.plugin_secret,
                              resource_owner_key=cfg.user_id,
                              resource_owner_secret=cfg.user_secret)
        protected_url = 'https://api.twitter.com/1.1/statuses/update.json'
        oauth.post(protected_url, params={"status": leaf.object})

    def valid_for_item(self, leaf):
        cfg = __kupfer_settings__[__CFG_KEY__]
        return cfg.user_secret and len(leaf.object) < 140

    def item_types(self):
        yield TextLeaf
