
#read plugin api:
# http://engla.github.io/kupfer/Documentation/PluginAPI.html

__kupfer_name__ = _("Marketplace")
__version__ = "0.1.0"
__author__ = "Hugo Sena Ribeiro <hugosenari@gmail.com>"
__description__ = _("""Search and install 3th party plugins for kupfer""")
__kupfer_sources__ = ("MarketplaceSource",)
__kupfer_actions__ = ("InstallPlugin",)
from kupfer.plugin_support import PluginSettings
__kupfer_settings__ = PluginSettings( 
    {
        "key" : "marketplace_keywords",
        "label": _("pypi search keywords"),
        "type": str,
        "value": "kupfer",
    },
    {
        "key" : "marketplace_index",
        "label": _("pypi index"),
        "type": str,
        "value": "https://pypi.python.org/pypi",
    }
)


def namelize(name):
    name = name or ''
    name = name.replace('kupfer_plugin_', '')
    name = name.replace('_', ' ')
    name = name.capitalize()
    return name


from kupfer.objects import Leaf
class PyPiPluginLeaf(Leaf):
    def __init__(self, obj):
        super(self.__class__, self).__init__(
            obj,
            namelize(obj.get('name')),
        )
        
    def get_description(self):
        return self.object.get('summary')


from kupfer import uiutils
from kupfer.objects import Action
from pip.commands.install import InstallCommand
class InstallPlugin(Action):
    def __init__(self):
        Action.__init__(self, name=_("Install"))
    
    def activate(self, leaf):
        InstallCommand().main(['--upgrade', '--user', leaf.object.get("name")] )
        uiutils.show_notification(_("Plugin Installed"), 
            "Now enable {} at preferences".format(leaf.name),
            icon_name=self.get_icon_name())

    def item_types(self):
        yield PyPiPluginLeaf

    def valid_for_item(self, leaf):
        return True


from kupfer.objects import Source
class MarketplaceSource(Source):
    def __init__(self):
        super(self.__class__, self).__init__(_("Plugin Marketplace"))
        self.my_resource = None
    
    #return the list of leaf
    def get_items(self):
        if not self.my_resource is None:
            keywords = __kupfer_settings__["marketplace_keywords"]
            for obj in self.my_resource.search(
                {'keywords': keywords},'or'
            ):
                yield PyPiPluginLeaf(obj)
    
    def initialize(self):
        try:
            import xmlrpclib
        except ImportError:
            import xmlrpc.client as xmlrpclib
        uri = __kupfer_settings__["marketplace_index"]
        self.my_resource = xmlrpclib.ServerProxy(uri)
