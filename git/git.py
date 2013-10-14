__kupfer_name__ = _("Git")
__version__ = "0.1"
__author__ = "hugosenari <hugosenari@gmail.com>"
__description__ = _("""
    Git plugin for kupfer
""")
__kupfer_actions__ = ('GitActions', 'GitkAction',
    'ChangeBranchAction', 'CreateBranchAction',
    'CommitAction', 'CommitRecursiveAction')


from kupfer.objects import Action, Leaf, FileLeaf, Source, \
    TextLeaf, TextSource
from kupfer import uiutils
from sh import git, gitk, ErrorReturnCode
import os


# utils function

def show_msg(msg, title='info'):
    uiutils.show_notification(title, msg)


def try_or_show_msg(fn):

    def wrapper(*args, **kwds):
        try:
            return fn(*args, **kwds)
        except ErrorReturnCode as e:
            show_msg(e.stderr or e, _('Error'))
    return wrapper


def generator(fn):

    def generated(*args, **kwds):
        items = fn(*args, **kwds)
        for item in items:
            yield item
    return generated


# actions

class GitActions(Action):

    def __init__(self):
        Action.__init__(self, _("Git Actions"))

    def activate(self, leaf):
        cwd = leaf.canonical_path() if leaf.is_dir else \
            os.path.dirname(leaf.canonical_path())
        return GitStatusLeaf(leaf, cwd)

    def item_types(self):
        yield FileLeaf

    def valid_for_item(self, leaf):
        cwd = leaf.canonical_path() if leaf.is_dir else \
            os.path.dirname(leaf.canonical_path())
        return git_is_repo_dir(cwd)

    def is_factory(self):
        return True

    def has_result(self):
        return True


class ChangeBranchAction(Action):

    def __init__(self):
        Action.__init__(self, _('Change Branch'))

    def item_types(self):
        yield GitStatusLeaf

    def activate(self, leaf, rleaf):
        git_ch_branch(leaf.cwd, rleaf.name, rleaf.remote, False)
        return GitStatusLeaf(leaf.object['file'], leaf.cwd)

    def object_types(self):
        yield GitBranchLeaf

    def object_source(self, for_item=None):
        return BranchSource(for_item)

    def requires_object(self):
        return True

    def is_factory(self):
        return True

    def has_result(self):
        return True


class CreateBranchAction(Action):

    def __init__(self):
        Action.__init__(self, _('Create Branch'))

    def item_types(self):
        yield GitStatusLeaf

    def activate(self, leaf, rleaf):
        git_ch_branch(leaf.cwd, rleaf.object, None)
        return GitStatusLeaf(leaf.object['file'], leaf.cwd)

    def object_types(self):
        yield TextLeaf

    def object_source(self, for_item=None):
        return TextSource()

    def requires_object(self):
        return True

    def is_factory(self):
        return True

    def has_result(self):
        return True


class CommitAction(Action):

    def __init__(self):
        Action.__init__(self, _('Commit'))

    def item_types(self):
        yield GitStatusLeaf

    def activate(self, leaf, rleaf):
        git_commit(leaf.cwd, rleaf.object, False)
        return GitStatusLeaf(leaf.object['file'], leaf.cwd)

    def object_types(self):
        yield TextLeaf

    def object_source(self, for_item=None):
        return TextSource()

    def requires_object(self):
        return True

    def is_factory(self):
        return True

    def has_result(self):
        return True


class CommitRecursiveAction(Action):

    def __init__(self):
        Action.__init__(self, _('Commit All In Dir'))

    def item_types(self):
        yield GitStatusLeaf

    def activate(self, leaf, rleaf):
        git_commit(leaf.cwd, rleaf.object)
        return GitStatusLeaf(leaf.object['file'], leaf.cwd)

    def object_types(self):
        yield TextLeaf

    def object_source(self, for_item=None):
        return TextSource()

    def requires_object(self):
        return True

    def is_factory(self):
        return True

    def has_result(self):
        return True


class GitkAction(Action):

    def __init__(self):
        Action.__init__(self, _("Gitk"))

    def item_types(self):
        yield GitStatusLeaf

    def activate(self, leaf):
        ''''''
        git_ui(leaf.cwd)


# Leaf

class GitStatusLeaf(Leaf):

    def __init__(self, obj, cwd=None):
        self.cwd = cwd
        self.status = git_status(self.cwd)
        self.branch = git_current_branch(self.cwd)
        self.root = str(git_root(self.cwd))
        self.name = os.path.basename(self.root) + ': ' + self.branch
        Leaf.__init__(self, {'file': obj}, self.name)

    def get_description(self):
        return _('Git Status: ') + \
            str(self.status).replace("{u'", "{'").replace(", u'", ", '") + \
            ': ' + self.cwd


class GitBranchLeaf(Leaf):

    def __init__(self, name, path, remote=None):
        Leaf.__init__(self,
            {'path': path, 'name': name, 'remote': remote},
            name)
        self.name = name
        self.path = path
        self.remote = remote
        self.is_remote = bool(remote)

    def get_description(self):
        return (self.remote or 'local') + ': ' + self.name


# sources

class BranchSource (Source):

    def __init__(self, obj=None):
        Source.__init__(self, _("Branch Source"))
        self.cwd = obj.cwd if obj else None

    def get_items(self):
        branches = fil_remove_link(git_branchs(self.cwd))
        for branch in branches:
            if 'remotes/' in branch:
                splited = branch.split('/')
                yield GitBranchLeaf(splited[2], self.cwd, splited[1])
            else:
                yield GitBranchLeaf(branch, self.cwd)

    def is_dynamic(self):
        return True


# git short-hands

@try_or_show_msg
def git_status(file_path):
    '''
        Return object with {key: count}, with a key for current status,
        and count of times for this status
    '''
    return count_status(
        fil_parse_status(
            fil_clean_output(
                gen_status(file_path))))


@try_or_show_msg
def git_branchs(file_path):
    '''Return all branchs'''
    return fil_clean_branch(
        fil_clean_output(
            gen_branchs(file_path)))


@try_or_show_msg
def git_current_branch(file_path):
    '''Return current branch'''
    return current_branch(
        fil_clean_output(
            gen_branchs(file_path)))


@try_or_show_msg
def git_remotes(file_path):
    '''Return a list of remotes'''
    return fil_clean_output(
        gen_remotes(file_path))


@try_or_show_msg
def git_ui(file_path):
    '''Show gitk for dir'''
    gitk(_cwd=file_path)


@try_or_show_msg
def git_ch_branch(file_path, branch, remote=None, create=True):
    '''Change current branch'''
    args = []
    if create:
        args.append('-b')
    if remote:
        branch = remote + '/' + branch
    args.append(branch)
    git.checkout(*args, _cwd=file_path)


@try_or_show_msg
def git_commit(file_path, message, recursive=True):
    '''Change current branch'''
    args = []
    if recursive:
        args.append('-a')
    args.append('-m')
    args.append(message)
    git.checkout(*args, _cwd=file_path)


@try_or_show_msg
def git_root(file_path):
    '''Return git root dir name'''
    rev_parse = git.bake('rev-parse')
    roots = rev_parse('--show-toplevel', _cwd=file_path)
    return fil_clean_output(roots).next()


def git_is_repo_dir(file_path):
    '''Return git root dir name'''
    rev_parse = git.bake('rev-parse')
    try:
        roots = rev_parse('--show-toplevel', _cwd=file_path)
        return bool(fil_clean_output(roots).next())
    except:
        return False


# git generators consumer

def count_status(all_parsed_status):
    '''return count of status'''
    result = {}
    for parsed_status in all_parsed_status:
        value = parsed_status['value']
        if not value in result:
            result[value] = 0
        result[value] = result[value] + 1
    return result


def current_branch(branchs):
    '''return current branch name'''
    for branch in branchs:
        if '*' in branch:
            return str(branch.split('* ')[1])


# git generators

@generator
def gen_remotes(file_path):
    '''return generetor of remotes'''
    remotes = git.remote(_cwd=file_path)
    return remotes


@generator
def gen_branchs(file_path):
    '''return generator with branchs'''
    branches = git.branch('--all', '--color=never', _cwd=file_path)
    return branches


@generator
def gen_status(file_path):
    '''return generator with result of git status --porcelain'''
    all_status = git.status('--porcelain', _cwd=file_path)
    return all_status


# generators filters

def fil_clean_output(lines):
    '''return generator with lines without space and \n '''
    for line in lines:
        yield line.strip(' ').strip('\n')


def fil_remove_link(lines):
    '''return generator without git "links"  '''
    for line in lines:
        if not '->' in line:
            yield line


def fil_parse_status(all_status):
    '''return generator with {'value': status, 'path': file}'''
    for status in all_status:
        splited = status.split(' ')
        value = splited[0]
        path = splited[1:]
        yield {'value': value, 'path': path}


def fil_clean_branch(branchs):
    '''Remove * from current branch'''
    for branch in branchs:
        if '*' in branch:
            yield str(branch.split('* ')[1])
        else:
            yield branch


def fil_remove_remote(branchs):
    '''Remove branchs with remote'''
    for branch in branchs:
        if not 'remotes/' in branch:
            yield branch


def fil_local_remote(branchs):
    '''Remove branchs withour remote'''
    for branch in branchs:
        if 'remotes/' in branch:
            yield branch
