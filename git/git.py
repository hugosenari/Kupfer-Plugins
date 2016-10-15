__kupfer_name__ = _("Git")
__version__ = "0.1.0"
__author__ = "hugosenari <hugosenari@gmail.com>"
__description__ = _("""Git plugin for kupfer""")
__kupfer_actions__ = ('GitActions', 'GitkAction', 'ChangeBranchAction',
    'CreateBranchAction', 'FetchBranchAction', 'PullBranchAction',
    'PushBranchAction', 'CommitAction', 'CommitRecursiveAction')


from kupfer.objects import Action, Leaf, FileLeaf, Source, \
    TextLeaf, TextSource
from kupfer import uiutils
from sh import git, gitk, ErrorReturnCode
from os import path


# utils function

_ = lambda x: x


def show_msg(msg, title='Info'):
    uiutils.show_notification(_(title), _(msg))


def try_or_show_msg(fn):

    def wrapper(*args, **kwds):
        try:
            return fn(*args, **kwds)
        except ErrorReturnCode as e:
            show_msg(e.stderr or e, 'Error')
    return wrapper


def generator(fn):

    def generated(*args, **kwds):
        items = fn(*args, **kwds)
        for item in items:
            yield item
    return generated


def dir_path(file_path):
    is_dir = path.isdir(file_path)
    parent_dir = path.dirname(file_path)
    result = file_path if is_dir else parent_dir
    return result


class GitActionMixin(object):

    def valid_for_item(self, leaf):
        abs_path = leaf.canonical_path()
        return git_is_repo_dir(abs_path)

    def item_types(self):
        yield FileLeaf
        yield GitStatusLeaf
        yield BranchSource

    def is_factory(self):
        return True

    def has_result(self):
        return True

    def activate(self, leaf, *args):
        git_status = GitStatusLeaf(leaf)
        return self._activate(git_status, *args)


class BranchActionMixin(object):

    def object_types(self):
        yield GitBranchLeaf

    def object_source(self, for_item=None):
        git_status = GitStatusLeaf(for_item)
        return BranchSource(git_status, self.branch_filter)

    def requires_object(self):
        return True


class TextActionMixin(object):

    def object_types(self):
        yield TextLeaf

    def object_source(self, for_item=None):
        return TextSource()

    def requires_object(self):
        return True


# actions

class GitActions(GitActionMixin, Action):

    def __init__(self):
        Action.__init__(self, _("Git Actions"))

    def _activate(self, leaf):
        return leaf


class ChangeBranchAction(GitActionMixin, BranchActionMixin, Action):

    def __init__(self):
        self.branch_filter = None
        Action.__init__(self, _('Change Branch'))

    def _activate(self, leaf, rleaf):
        git_ch_branch(leaf.abs_path, rleaf.name, rleaf.remote, False)
        return GitStatusLeaf(leaf)


class FetchBranchAction(GitActionMixin, BranchActionMixin, Action):

    def __init__(self):
        self.branch_filter = fil_remove_local
        Action.__init__(self, _('Fetch'))

    def _activate(self, leaf, rleaf):
        git_fetch(rleaf.remote, rleaf.name, leaf.abs_path)
        return GitStatusLeaf(leaf)


class PullBranchAction(GitActionMixin, BranchActionMixin, Action):

    def __init__(self):
        self.branch_filter = fil_remove_local
        Action.__init__(self, _('Pull'))

    def _activate(self, leaf, rleaf):
        git_pull(rleaf.remote, rleaf.name, leaf.abs_path)
        return GitStatusLeaf(leaf)


class PushBranchAction(GitActionMixin, BranchActionMixin, Action):

    def __init__(self):
        self.branch_filter = fil_remove_local
        Action.__init__(self, _('Push'))

    def activate(self, leaf, rleaf):
        git_push(rleaf.remote, rleaf.name, leaf.abs_path)


class CreateBranchAction(GitActionMixin, TextActionMixin, Action):

    def __init__(self):
        Action.__init__(self, _('Create Branch'))

    def _activate(self, leaf, rleaf):
        git_ch_branch(leaf.abs_path, rleaf.object, None)
        return GitStatusLeaf(leaf)


class CommitAction(GitActionMixin, TextActionMixin, Action):

    def __init__(self):
        Action.__init__(self, _('Commit'))

    def _activate(self, leaf, rleaf):
        leaf = GitStatusLeaf(leaf)
        git_commit(leaf.abs_path, rleaf.object, False)
        return GitStatusLeaf(leaf)

    def valid_for_item(self, leaf):
        result = GitActionMixin.valid_for_item(self, leaf)
        if result:
            leaf = GitStatusLeaf(leaf)
            result = git_has_changes(leaf.abs_path)
        return result


class CommitRecursiveAction(GitActionMixin, TextActionMixin, Action):

    def __init__(self):
        Action.__init__(self, _('Commit All In Dir'))

    def _activate(self, leaf, rleaf):
        git_commit(leaf.abs_path, rleaf.object, leaf.file_name)
        return GitStatusLeaf(leaf)

    def valid_for_item(self, leaf):
        result = GitActionMixin.valid_for_item(self, leaf)
        if result:
            leaf = GitStatusLeaf(leaf)
            result = git_has_changes(dir_path(leaf.abs_path))
        return result


class GitkAction(GitActionMixin, Action):

    def __init__(self):
        Action.__init__(self, _("Gitk"))

    def _activate(self, leaf):
        ''''''
        git_ui(leaf.abs_path)
        return GitStatusLeaf(leaf)


# Leaf

class GitStatusLeaf(Leaf):

    def __init__(self, leaf):
        real_path = leaf.canonical_path()
        leaf_dict = file_dict(real_path)
        self.root = leaf_dict['root']
        self.title = leaf_dict['title']
        self.status = leaf_dict['status']
        self.branch = leaf_dict['branch']
        self.abs_path = leaf_dict['abs_path']
        self.description = leaf_dict['description']
        Leaf.__init__(self, leaf.object, self.title)

    def get_description(self):
        return self.description

    def canonical_path(self):
        return self.abs_path


class GitBranchLeaf(Leaf):

    def __init__(self, name, path, remote=None):
        Leaf.__init__(self,
            {'path': path, 'name': name, 'remote': remote},
            name)
        self.name = name
        self.abs_path = path
        self.remote = remote
        self.is_remote = bool(remote)

    def canonical_path(self):
        return self.abs_path

    def get_description(self):
        return (self.remote or 'local') + ': ' + self.name


# sources

class BranchSource(Source):

    def __init__(self, obj=None, fil=None):
        Source.__init__(self, _("Branch Source"))
        self.fil = fil or (lambda x: (y for y in x))
        self.abs_path = obj.abs_path if obj else None

    def get_items(self):
        fil = self.fil
        branches = fil(fil_remove_link(git_branchs(self.abs_path)))
        for branch in branches:
            if 'remotes/' in branch:
                splited = branch.split('/')
                yield GitBranchLeaf(splited[2], self.abs_path, splited[1])
            else:
                yield GitBranchLeaf(branch, self.abs_path)

    def is_dynamic(self):
        return True


# kupfer short-hand

def file_dict(real_path):
    result = {}
    result['abs_path'] = real_path

    result['root'] = str(git_root(real_path))
    result['status'] = git_status(real_path)
    result['branch'] = git_current_branch(real_path)

    result['title'] = path.basename(real_path) + ': ' + result['branch']

    result['description'] = _('Git Status: ') + \
        str(result['status']).replace("{u'", "{'").replace(", u'", ", '") + \
        ': ' + path.basename(result['root'])

    return result


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


def git_has_changes(file_path):
    try:
        statuses = fil_remove_status_value(
            fil_parse_status(
                fil_clean_output(
                    gen_status(file_path))), '??')
        for status in statuses:
            return True
    except Exception as e:
        return False


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
    gitk(_cwd=dir_path(file_path))


@try_or_show_msg
def git_ch_branch(file_path, branch, remote=None, create=True):
    '''Change current branch'''
    args = []
    if create:
        args.append('-b')
    if remote:
        branch = remote + '/' + branch
    args.append(branch)
    git.checkout(*args, _cwd=dir_path(file_path))
    show_msg('Now at ' + branch, 'Info')


@try_or_show_msg
def git_fetch(remote, branch, file_path):
    '''Fetch for remote changes'''
    p = git.fetch(remote, branch, _cwd=dir_path(file_path), _tty_out=False)
    p.wait()
    show_msg('Repo updated', 'Info')


@try_or_show_msg
def git_pull(remote, branch, file_path):
    '''Pull remote changes'''
    p = git.pull(remote, branch, _cwd=dir_path(file_path), _tty_out=False)
    p.wait()
    show_msg('Pull Done', 'Info')


@try_or_show_msg
def git_push(remote, branch, file_path):
    '''Push changes to remote'''
    p = git.push(remote, branch, _cwd=dir_path(file_path), _tty_out=False)
    p.wait()
    show_msg('Push Done', 'Info')


@try_or_show_msg
def git_commit(file_path, message, recursive=True):
    '''Change current branch'''
    args = []
    if recursive:
        args.append('-a')
        file_path = dir_path(file_path)
    args.append('-m')
    args.append('"' + message + '"')
    args.append(file_path)
    git.commit(*args, _cwd=dir_path(file_path))
    show_msg('Commit Done', 'Info')


@try_or_show_msg
def git_root(file_path):
    '''Return git root dir name'''
    rev_parse = git.bake('rev-parse')
    roots = rev_parse('--show-toplevel', _cwd=dir_path(file_path))
    return fil_clean_output(roots).next()


def git_is_repo_dir(file_path):
    '''Return git root dir name'''
    rev_parse = git.bake('rev-parse')
    try:
        roots = rev_parse('--show-toplevel', _cwd=dir_path(file_path))
        return bool(fil_clean_output(roots).next())
    except Exception as e:
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
    remotes = git.remote(_cwd=dir_path(file_path))
    return remotes


@generator
def gen_branchs(file_path):
    '''return generator with branchs'''
    branches = git.branch('--all', '--color=never', _cwd=dir_path(file_path))
    return branches


@generator
def gen_status(file_path):
    '''return generator with result of git status --porcelain'''
    all_status = git.status('--porcelain', file_path, _cwd=dir_path(file_path))
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


def fil_remove_status_value(all_status, value):
    '''filter parsed status by status[value]'''
    for status in all_status:
        if status['value'] != value:
            yield status


def fil_remove_parent(branchs):
    '''Remove status with .. from list'''
    for branch in branchs:
        if not '..' in branch:
            yield branch


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


def fil_remove_local(branchs):
    '''Remove branchs withour remote'''
    for branch in branchs:
        if 'remotes/' in branch:
            yield branch
