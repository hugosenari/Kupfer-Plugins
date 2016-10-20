# -*- coding: UTF-8 -*-
__author__ = u"Hugo Sena Ribeiro <hugosenari gmail com>"
__description__ = _("""Start remmina sessions""")
__kupfer_actions__ = (u"RemminaConnect",)
__kupfer_name__ = _(u"Remmina")
__kupfer_sources__ = (u"ReminaHostServiceSource",)
__version__ = "0.1.2"

from kupfer import pretty, utils
from kupfer.obj.apps import AppLeafContentMixin
from kupfer.objects import Action
from kupfer.obj.grouping import ToplevelGroupingSource
from kupfer.obj.helplib import FilesystemWatchMixin
from kupfer.obj.hosts import HostLeaf, HostServiceLeaf
from kupfer.plugin_support import PluginSettings
import fnmatch
import os
import re

home_dir = os.getenv('USERPROFILE') or os.getenv('HOME')

default_cfg_dir1 = os.path.join(home_dir, '.remmina')
default_cfg_dir2 = os.path.join(home_dir, '.local', 'share', 'remmina')
default_cfg_dir = ':'.join([default_cfg_dir1, default_cfg_dir2])

__kupfer_settings__ = PluginSettings( 
        {
                "key" : "remmina_hosts_folder",
                "label": _("Remina config folders"),
                "type": str,
                "value": default_cfg_dir,
        }
)

class ReminnaHostServiceLeaf(HostServiceLeaf):
    def __init__(self, item):
        HostServiceLeaf.__init__(self,
             item.get('name'),
             item.get('server') or item.get('ssh_server'),
             item.get('protocol'),
             item.get('description'),
             item.get('port'),
             item.get('username') or item.get('ssh_username'),
             item.get('password') or item.get('ssh_password'),
             item
        )

    def get_icon_name(self):
        return "network-server"


class ReminaHostServiceSource(AppLeafContentMixin,
                ToplevelGroupingSource, FilesystemWatchMixin):
    '''Remmina leaf factory'''
    appleaf_content_id = 'remmina'
    
    def __init__(self, name=_("Remmina Hosts")):
        ToplevelGroupingSource.__init__(self, name, _("Remmina"))

    def initialize(self):
        ToplevelGroupingSource.initialize(self)
        cfg_dir = __kupfer_settings__["remmina_hosts_folder"]
        self.monitor_token = self.monitor_directories(cfg_dir)    

    def provides(self):
        yield ReminaHostServiceSource

    def get_description(self):
        return __description__

    def get_icon_name(self):
        return "remmina"

    def get_items(self):
        files = ReminaHostServiceSource.list_files() or []
        for host_file in files:
            item = ReminaHostServiceSource._parse_file(host_file)
            yield ReminnaHostServiceLeaf(item)
    
    @staticmethod
    def list_files():
        cfg_dirs = __kupfer_settings__["remmina_hosts_folder"]
        for cfg_dir in cfg_dirs.split(':'):
            cfg_files = []
            if os.path.exists(cfg_dir):
                cfg_files = os.listdir(cfg_dir)
            for cfg_file in cfg_files:
                if fnmatch.fnmatch(cfg_file, '*.remmina'):
                    yield os.path.join(cfg_dir, cfg_file)

    @staticmethod
    def _parse_file(uri):
        result = {'path': uri}
        with open(uri) as cfg_file:
            reg = re.compile("\s*([^=]+)\s*=\s*(.+)\s*")
            for line in cfg_file.readlines():
                match = reg.match(line)
                if match:
                    key, value = match.groups()
                    result[key] = value.strip()

        result['description'] = "%s : %s : %s : %s" % (
            result.get('group', 'no group'),
            result.get('server') or result.get('ssh_server'),
            result.get('protocol'),
            result.get('name'))
        pretty.print_debug(__name__, result['description'])
        return result


class RemminaConnect(Action):
    '''Used to launch remmina connecting to the specified config file.'''
    def __init__(self):
        Action.__init__(self, name=_("Connect (Remmina)"))

    def get_description(self):
        return _("Connect with Remmina")

    def get_icon_name(self):
        return "remmina"

    def item_types(self):
        yield ReminnaHostServiceLeaf

    def valid_for_item(self, leaf):
        """Whether action can be used with exactly @item"""
        return leaf.check_key('path')\
            or leaf.check_key('TSCLIENT_SESSION')

    def activate(self, leaf):
        obj = leaf.object
        if obj.get('path') or obj.get('TSCLIENT_SESSION'):
            utils.spawn_async(("remmina", "-c",
                obj.get('path') or obj.get('TSCLIENT_SESSION')))
