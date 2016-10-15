
#read plugin api:
# http://engla.github.io/kupfer/Documentation/PluginAPI.html

__kupfer_name__ = _("PLUGIN_NAME")
__version__ = "0.2"
__author__ = "YOUR_NAME <YOUR@EMAIL>"
__description__ = _("""
    PLUGIN_DESCRIPTION
""")

#optional:
# should be tuples of names of classes in the plugin
#__kupfer_sources__ = ("YourPluginSource",)
#__kupfer_actions__ = ("PluginActionName",)
#other options:
#__kupfer_text_sources__ = ("PLUGIN_TEXT_SOURCES",)
#__kupfer_action_generators__ = ("PLUGIN_ACTION_GENERATORS",)
#__kupfer_contents__ = ("PLUGIN_CONTENTS",)

#if your plugin needs user settings
#from kupfer.plugin_support import PluginSettings
#__kupfer_settings__ = PluginSettings( 
#    {
#        "key" : "SETTING_KEY",
#        "label": _("SETTING_LABEL"),
#        "type": str,
#        "value": "SETTING_DEFAULT_VALUE",
#    }, 
#    {
#        "key" : "OTHER_SETTING_KEY",
#        "label": _("OTHER_SETTING_LABEL"),
#        "type": int,
#        "value": "OTHER_SETTING_DEFAULT_VALUE",
#        "alternatives": OTHER_SETTING_LIST_OF_ALTERNATIVES
#    },
#)
#then you can get setting:
#__kupfer_settings__["SETTING_KEY"]


#PLUGINS LEAFS
#leafs are plugin objects
#ie: TextLeaf, FileLeaf, ContactLeaf, EmailLeaf, FolderLeaf, ApplicationLeaf...
#from kupfer.objects import Leaf
#class YourPluginLeaf(Leaf):
#    #required
#    #init your leaf object
#    def __init__(self, obj):
#        ''' '''
#        super(self.__class__, self).__init__(obj, _("Plugin Leaf Name"))
#        #do something else with object
#        #you can get object anywhere in this class using self.object
#
#    #optional
#    #return list of actions that can work with this object
#    def get_actions(self):
#        ''' '''
#        yield Plugin_Action_name


#PLUGIN ACTIONS
#actions are what your plugin can do with objects
#ie: OpenFile, Delete, Edit, PlayNext...
#from kupfer.objects import Action
#class PluginActionName(action):
#    #required
#    #do here something with your object
#    def activate(self, obj):
#        ''' '''
#        #obj in most of case are a leaf
#        
#
#    #optional
#    #return list of object that can be activated with this
#    #reverse version of get_actions defined in leaf
#    def item_types(self):
#        ''' '''


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