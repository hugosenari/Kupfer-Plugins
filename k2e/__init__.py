#-*- coding: UTF-8 -*-
## baseado no código do plugin para twitter
from __future__ import absolute_import
__kupfer_name__ = _('k2e')
__kupfer_sources__ = ('ProjectsSource', 'ExecutesSource', 'MvnSource')
__kupfer_actions__ = ('Run', 'Debug', 'Open', 'Close', 'Test', 'Mvn')
__description__ = _('Eclipse Plugin to Kupfer')
__version__ = '2011-01-22'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'

import os
from kupfer import icons, pretty
from kupfer import plugin_support
from kupfer import kupferstring
from kupfer.objects import Action, TextLeaf, Source, SourceLeaf, TextSource
from kupfer.obj.grouping import ToplevelGroupingSource
from kupfer.obj.special import PleaseConfigureLeaf

__kupfer_settings__ = plugin_support.PluginSettings(
    {
        'key': 'workspacePath',
        'label': _('Workspace file path'),
        'type': str,
        'value': '~/workspace',
    },
    {
        'key': 'runInTerminal',
        'label': _("Run in terminal"),
        'type': bool,
        'value': True,
    },
    {
        'key': 'enableMaven',
        'label': _("Enable maven"),
        'type': bool,
        'value': False,
    }
)

UPDATE_INTERVAL_S = 15
PROJECTS_NAME_KEY = 'eclipse_workspace'

def get_profects_config_dirs(config_dir_path):
    projects_dir_path = configs_dir_path + '/org.eclipse.core.resources/.projects'
    return os.listdir(projects_dir_path)

def load_file_config(config_file):
    if not __kupfer_settings__['workspacePath']:
        return None
    configs_dir_path = __kupfer_settings__['workspacePath']+'/.metadata/.plugins'
    

class ProjectsSource(ToplevelGroupingSource):
    grouping_slots = ContactLeaf.grouping_slots + (PROJECTS_NAME_KEY, )
    def __init__(self, path, name, image=None):
        slots = {PROJECTS_NAME_KEY: name, NAME_KEY: name}
        ContactLeaf.__init__(self, slots, name)
        self.kupfer_add_alias(name)
        self.image = image
        self.projects = None

    def repr_key(self):
        return self.object[PROJECTS_NAME_KEY]

    def has_content(self):
        return bool(self.projects) or ContactLeaf.has_content(self)

    def content_source(self, alternate=False):
        if ContactLeaf.has_content(self):
            return ContactLeaf.content_source(self, alternate=alternate)
        if self.projects:
            return ProjectsStatusesSource(self)

    def get_description(self):
        return self[PROJECTS_NAME_KEY]


class ProjectsStatusesSource(Source):
    def __init__(self, project):
        name = _("Timeline for %s") % project
        Source.__init__(self, name)
        self.project = project

    def get_items(self):
        return self.friend.tweets

    def get_icon_name(self):
        return 'eclipse'

    def provides(self):
        yield StatusLeaf

    def has_parent(self):
        return True