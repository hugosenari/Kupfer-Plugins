## read plugin api:
## https://kupferlauncher.github.io/Documentation/PluginAPI.html

__kupfer_name__ = _('GTKIcons')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''List all gtk icons available'''
__kupfer_sources__ = ("GtkIconSource",)

from kupfer.objects import TextLeaf
from kupfer.objects import Source
from kupfer import pretty
from os import path
from gi.repository import Gtk
from subprocess import check_output


class GtkIconLeaf(TextLeaf):

    def __init__(self, obj):
        TextLeaf.__init__(self, obj)

    def get_icon_name(self):
        return self.object

    def get_description(self):
        return "GTK ICON: " + self.object

  
class GtkIconSource(Source):

    def __init__(self):
        Source.__init__(self, _("GTk Icons"))

    def icons_list(self):
        return check_output(["find", "/usr/share/icons", "-type", "f"])

    def is_icon(self, fila_name):
        parts = fila_name.split(b'.')
        if len(parts) == 2: 
            if parts[1] in (b'png', b'xpn', b'svg'):
                return parts[0].decode(errors="ignore")

    def get_items(self):
        gone = {}
        for obj in Gtk.stock_list_ids():
            gone[obj] = 1
            yield GtkIconLeaf(obj)
        try:
            icons = self.icons_list()
            for l in icons.split(b'\n'):
                file_name = path.basename(l)
                icon_name = self.is_icon(file_name)
                if icon_name and icon_name not in gone:
                    gone[icon_name] = 1
                    yield GtkIconLeaf(icon_name)
        except Exception as e:
            pretty.print_error(__name__, type(e).__name__, e)

    def provides(self):
        yield GtkIconLeaf

    def get_icon_name(self):
        return "gtk-directory"
