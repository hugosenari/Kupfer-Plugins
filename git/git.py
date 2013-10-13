__kupfer_name__ = _("Git")
__version__ = "0.1"
__author__ = "hugosenari <hugosenari@gmail.com>"
__description__ = _("""
    Git plugin for kupfer
""")
__kupfer_actions__ = ('GitActions', 'GitkAction')


from kupfer.objects import Leaf, FileLeaf #, TextLeaf
from kupfer.obj.base import Action
from kupfer import uiutils
import sh
import os


class GitActions(Action):
    ''' '''

    def __init__(self):
        Action.__init__(self, _("Git Actions"))

    def activate(self, obj):
        ''' '''
        return GitStatusLeaf(obj)

    def item_types(self):
        ''' '''
        yield FileLeaf

    def has_result(self):
        return True

    def valid_for_item(self, leaf):
        cwd = leaf.canonical_path() if leaf.is_dir else \
            os.path.dirname(leaf.canonical_path())
        status = git_status(cwd)
        try:
            return status.next()
        except:
            return False


class GitStatusLeaf(Leaf):
    ''' '''

    def __init__(self, obj):
        ''' '''
        Leaf.__init__(self, {'file': obj}, _("Git Status"))
        self.cwd = obj.canonical_path() if obj.is_dir else \
            os.path.dirname(obj.canonical_path())
        self.status = git_count_status(git_parse_status(git_status(self.cwd)))

    def get_description(self):
        return str(self.status)


class GitkAction(Action):
    ''' '''

    def __init__(self):
        Action.__init__(self, _("Show with Gitk"))

    def item_types(self):
        yield GitStatusLeaf

    def activate(self, leaf):
        ''''''
        try:
            sh.gitk(_cwd=leaf.cwd)
        except sh.ErrorReturnCode as e:
            show_msg(e.stderr, "Error")


def git_status(file_path):
    all_status = sh.git.status('--porcelain', _cwd=file_path)
    for status in all_status:
        yield status.strip(' ').strip('\n')


def git_parse_status(all_status):
    for status in all_status:
        splited = status.split(' ')
        value = splited[0]
        path = splited[1:]
        yield {'value': value, 'path': path}


def git_count_status(all_parsed_status):
    result = {}
    for parsed_status in all_parsed_status:
        value = parsed_status['value']
        if not value in result:
            result[value] = 0
        result[value] = result[value] + 1
    return result


def show_msg(msg, title='info'):
    uiutils.show_notification(title, msg)
