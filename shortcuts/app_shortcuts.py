__kupfer_name__ = _("Apps Shortcuts")
__kupfer_sources__ = ("ShortcutSources",)
__kupfer_actions__ = ("ShowShortcut", "Execute") #, "Add", "Remove")
__description__ = _("""Kupfer plugin to learn apps shortcuts.
Using xdotool to execute

Special thanks to
eclipse-tools.sourceforge.net
source of shortcuts
""")
__version__ = "0.1"
__author__ = "Hugo Sena Ribeiro <hugosenari gmail com>"

import json, os
from kupfer import utils, uiutils, pretty
from kupfer.plugin_support import PluginSettings
from kupfer.obj.base import Action, Leaf
from kupfer.obj.grouping import ToplevelGroupingSource

__kupfer_settings__ = PluginSettings( 
    {
        "key" : "shortcuts_source_path",
        "label": _("Path do shortcut source file"),
        "type": str,
        "value": "~/.local/share/kupfer/plugins/shortcuts.xdotool.json",
    },
)

#the sources
class ShortcutSources (ToplevelGroupingSource):
    def __init__(self):
        ToplevelGroupingSource.__init__(self, _("Shortcuts"), "shortcuts")
        self._version = 1
        self.shortcuts = {}
    
    def initialize(self):
        ToplevelGroupingSource.initialize(self)
        try:
            shortcutsFile = open(os.path.expanduser(__kupfer_settings__["shortcuts_source_path"]), 'r')
            try:
                self.shortcuts = json.load(shortcutsFile)["shortcuts"]
            except Exception:
                pretty.print_debug(__name__, "xi")
            shortcutsFile.close()
        except Exception:
            pretty.print_debug(__name__, "xixi")
            
    def get_items(self):
        for item in self.shortcuts:
            yield ShortcutLeaf(item)
  
    def get_icon_name(self):
        return "key_bindings"

#the 'objects'
class ShortcutLeaf (Leaf):
    """ Leaf represent shortcut"""
    def __init__(self, shortcut):
        Leaf.__init__(self, shortcut, _(u" %s (%s)" % (shortcut["desc"], shortcut["keys"])))
        self.desc = shortcut["desc"]
        
    def get_actions(self):
        yield ShowShortcut()

    def repr_key(self):
        return self.object["keys"]
    
    def get_decription(self):
        return u"%s" % (self.object["desc"])

    def get_text_representation(self):
        return u"%s (%s)" % (self.object["desc"], self.object["keys"])

    def get_icon_name(self):
        return "key_bindings"
        
    def text_with_key(self):
        yield TextLeaf(self.repr_key())
        
    def text_with_desc(self):
        yield TextLeaf(self.get_decription())
    
#the actions actions actions actions actions 
class ShowShortcut(Action):
    def __init__(self):
        Action.__init__(self, _("Show shortcut"))
    
    def item_types(self):
        yield ShortcutLeaf

    def get_description(self):
        return _("Display this")

    def get_icon_name(self):
        return "format-text-bold"
    
    def activate(self, leaf):
        shortcut = leaf.object
        uiutils.show_notification(shortcut['keys'], shortcut['desc'],
            icon_name=self.get_icon_name())

class Execute(Action):
    def __init__(self):
        Action.__init__(self, _("Execute shortcuts"))
    
    def item_types(self):
        yield ShortcutLeaf

    def get_description(self):
        return _("Execute this")
    
    def activate(self, leaf):
        shortcut = leaf.object
        args = "xdotool search --class \"eclipse\" windowactivate --sync key --clearmodifiers \"%s\"" % shortcut['keys'].lower()
        argv = ['sh', '-c', args, '--']
        def finish_callback(acommand, stdout, stderr):
            pretty.print_debug(__name__, "%s: stdout: %s, stderr: %s, shortcut: %s" % (acommand, stdout, stderr, shortcut['keys'].lower()))
        utils.AsyncCommand(argv, finish_callback, 15)
        uiutils.show_notification(shortcut['keys'], shortcut['desc'],
            icon_name=self.get_icon_name())

# ROADMAP
# 0.1 show shortcuts for eclipse in notification
# 1.0 show shortcuts for any in notification
# UNSORTED future possible features:
# - read / import shortcuts from server maybe using DICT protocol
# - execute this shortcut at app
# - edit shortcuts file/online
# - use sqlite for database
# - suggestions? :)