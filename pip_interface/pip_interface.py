
#read plugin api:
# http://engla.github.io/kupfer/Documentation/PluginAPI.html

__kupfer_name__ = _("pip Interface")
__version__ = "0.1.0"
__author__ = "Hugo Sena Ribeiro <hugosenari@gmail.com>"
__description__ = _("""
    Run pip commands (search, install...) commands with kupfer
""")

#optional:
# should be tuples of names of classes in the plugin
__kupfer_sources__ = ("PyPiSource",)
__kupfer_actions__ = ("InstallAction", "SearchPackageAction", "UninstallAction")

#if your plugin needs user settings
from kupfer.plugin_support import PluginSettings
__kupfer_settings__ = PluginSettings( 
    {
        "key" : "pip_interface_index_uri",
        "label": _("PyPi Index"),
        "type": str,
        "value": "https://pypi.python.org/simple",
    },
    {
        "key" : "pip_interface_target",
        "label": _("Target Directory"),
        "type": str,
        "value": None,
    },
    {
        "key" : "pip_interface_root",
        "label": _("Root Directory"),
        "type": str,
        "value": None,
    },
)

def convert_param(name):
    name = name.replace('"pip_interface_','')
    name = name.replace('_', '-')
    name = '--' + name
    return name

def get_params():
    params = []
    for key, val in __kupfer_settings__.items():
        param = convert_param(key)
        if val:
            params.append(param)
            params.append(val)
    return params
    

from kupfer.objects import Leaf
class YourPluginLeaf(Leaf):
    def __init__(self, obj):
        Leaf.__init__(obj, _("Plugin Leaf Name"))

    def get_actions(self):
        yield InstallAction
        yield UninstallAction


from kupfer.objects import Action
from kupfer.objects import TextLeaf
from pip.commands.install import InstallCommand
class InstallAction(Action):
    def __init__(self):
        Action.__init__(self, name=_("Install Package"))

    def activate(self, leaf):
        params = get_params()
        if 'name' in leaf.object:
            params.append(leaf.object['name'])
        else:
            params.append(str(leaf.object))
        InstallCommand().main(params)

    def valid_for_item(self, leaf):
        return bool(leaf)

    def item_types(self):
        yield TextLeaf


class UninstallAction(Action):
    def __init__(self):
        Action.__init__(self, name=_("Uninstall Package"))

    def activate(self, obj):
        ''' '''

    def valid_for_item(self, leaf):
        return bool(leaf)

    def item_types(self):
        yield TextLeaf


class SearchPackageAction(Action):
    def __init__(self):
        Action.__init__(self, name=_("Action Name"))

    def activate(self, obj):
        ''' '''

    def valid_for_item(self, leaf):
        return bool(leaf)

    def item_types(self):
        yield TextLeaf


#PLUGIN_SOURCES
#from kupfer.objects import Source
#source are leaf factory
#here is where kupfer will create your leafs
#ie: TextsSource, FilesSource, ContactsSource, ApplicationsSource...
#from kupfer.objects import Source
#class YourPluginSource(Source):
#    #required
#    #init your source object
#    def __init__(self):
#        ''' '''
#        super(self.__class__, self).__init__(_("Plugin Source Name"))
#        self.resource = None
#    
#    #return the list of leaf
#    def get_items(self):
#        ''' '''
#        #note that you this example don't define MyPluginResource
#        #beause you doesn't need one, you can create all object inside this class
#        #than MyPluginResource this is only for ilustration
#        if self.resource:
#            for obj in self.resource.get_all():
#                yield YourPluginLeaf(obj)
#    
#    #optional
#    #start one or more resources that need to be started to get leaf
#    #ie: connect with one db, open file, ...
#    def initialize(self):
#        ''' '''
#        self.resource = MyPluginResource("")
#        self.resource.initialize()
#        
#    #optional
#    #stops resources created at "initialize"
#    def finalize(self):
#        ''' '''
#        if self.resource:
#            self.resource.finalize()
#            self.resource = None
