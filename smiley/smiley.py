__kupfer_name__ = _("Smiley")
__kupfer_sources__ = ("SmileySource",)
__kupfer_actions__ = ()
__description__ = _("""List and copy char of pidgin smiley theme""")
__version__ = "0.1"
__author__ = "Hugo Sena Ribeiro <hugosenari gmail com>"

from os import path
from kupfer import pretty, icons
from kupfer.plugin_support import PluginSettings
from kupfer.objects import Source, TextLeaf

__kupfer_settings__ = PluginSettings( 
    {
        "key" : "smiley_source_path",
        "label": _("Path of smiley theme"),
        "type": str,
        "value": "/usr/share/pixmaps/pidgin/emotes/default/",
    },
)

#the sources
class SmileySource (Source):
    def __init__(self):
        Source.__init__(self, _("Smiley"))
            
    def get_items(self):
        cfg = __kupfer_settings__["smiley_source_path"]
        theme_dir = path.expanduser(cfg)
        theme_path = path.join(theme_dir, 'theme')
        
        self._theme_exists(theme_path)
        
        with open(theme_path, 'r') as theme_file:
            for line in theme_file:
                smiley = self._smile(line, theme_dir)
                if smiley:
                    yield smiley
    
    def _theme_exists(self, theme_path):
        if not path.exists(theme_path):
            pretty.print_debug(__name__, "StopIteration not found " + theme_path)
            raise StopIteration()
    
    def _smile(self, line, theme_dir):
        values = self._values(line)
        if values:
            img = path.join(theme_dir, values[0])
            key = values[-1]
            names = values[0:]
            if path.exists(img):
                return SmileyLeaf(img, key, values)
    
    def _values(self, line):
        if line\
            and u'.png' in line\
            and not line.startswith(u'#')\
            and not line.startswith(u'[')\
            and not line.startswith(u'Icon=')\
            and not line.startswith(u'Icon ='):
            values = line.lstrip(u'!').split()
            if len(values) > 1:
                return values
        return None
  
    def get_icon_name(self):
        return "face-smile"


#the 'objects'
class SmileyLeaf (TextLeaf):
    """ Leaf represent shortcut"""
    def __init__(self, img, key, names):
        TextLeaf.__init__(self,
            key,
            u' '.join(names)
        )
        self._img = img

    def get_thumbnail(self, width, height):
        return icons.get_pixbuf_from_file(self._img, width, height)
