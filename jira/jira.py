
## read plugin api:
## https://kupferlauncher.github.io/Documentation/PluginAPI.html

__kupfer_name__ = 'Jira'
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''Kupfer plugin to control Jira'''

__kupfer_sources__ = ("ProjectSource",)
__kupfer_actions__ = ("Issue", "Show", "Close", "Assign", "Comment", "Search")

from kupfer.plugin_support import \
    PluginSettings, check_keyring_support, UserNamePassword
check_keyring_support()

__kupfer_settings__ = PluginSettings( 
    {
        "key" : "jira_login",
        "label": _("Login"),
        "type": plugin_support.UserNamePassword
    }, 
    {
        "key" : "jira_default_project",
        "label": _("Default Project"),
        "type": str
    }
)
## then you can get setting:
##__kupfer_settings__["jira_KEY"]

from kupfer.objects import Leaf 


class IssueLeaf(Leaf):
    def __init__(self, obj, jira):
        super(Leaf, self).__init__(obj, obj.key)
        self.jira = jira
        
    def description(self):
        return this.obj.fields.summary


class ProjectLeaf(Leaf):
    def __init__(self, obj, jira):
        super(Leaf, self).__init__(obj, obj.key)
        self.jira = jira
        
    def description(self):
        return this.obj.name


## PLUGIN ACTIONS
## actions are what your plugin can do with objects
## ie: OpenFile, Delete, Edit, PlayNext...
#from kupfer.objects import Action
#class PluginActionName(Action):
#    #required
#
#    def __init__(self):
#        Action.__init__(self, name=_("Action Name"))
#
#    #do here something with your object
#    def activate(self, obj):
#        ''' '''
#        #obj in most of case are a leaf
#
#    #optional
#    #Whether action can be used with exactly @item
#    def valid_for_item(self, leaf):
#        ''' '''
#        return bool(leaf)
#
#    #return list of object that can be activated with this
#    #reverse version of get_actions defined in leaf
#    def item_types(self):
#        ''' '''


from kupfer.objects import Source
class ProjectSource(Source):
    #required
    #init your source object
    def __init__(self):
        super(Source, self).__init__(_("Jira Projects"))
        self.resource = None
    
    #return the list of leaf
    def get_items(self):
        ''' '''
        #note that you this example don't define MyPluginResource
        #beause you doesn't need one, you can create all object inside this class
        #than MyPluginResource this is only for ilustration
        if self.resource:
            for obj in self.resource.get_all():
                yield YourPluginLeaf(obj)
    
    #optional
    #start one or more resources that need to be started to get leaf
    #ie: connect with one db, open file, ...
    def initialize(self):
        from jira import JIRA
        self.resource = MyPluginResource("")
        self.resource.initialize()
