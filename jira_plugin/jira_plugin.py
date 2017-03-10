__kupfer_name__ = _('Jira')
__version__ = '0.1.3'
__author__ = _('Hugo Sena Ribeiro <hugosenari@gmail.com>')
__description__ = _('''Kupfer plugin to control Jira''')

__kupfer_sources__ = ("ProjectSource",)
__kupfer_actions__ = ("Issue", "Show", "Comment", "Assign", "ChangeStatus")


import re
from jira import JIRA
from jira import Issue as issue
from jira import Project as project
from kupfer.utils import show_url
from kupfer.objects import Leaf
from kupfer.objects import Source
from kupfer.objects import Action, TextLeaf
from kupfer.plugin_support import \
    PluginSettings, check_keyring_support, UserNamePassword


check_keyring_support()

__kupfer_settings__ = PluginSettings( 
    {
        "key" : "jira_login",
        "label": "Login",
        "type": UserNamePassword,
        "value": None
    },
    {
        "key" : "jira_url",
        "label": "Jira URL",
        "type": str,
        "value": ""
    }
)
FIELD_WHITE_LIST = (
    'labels',
    'priority',
    'timespent',
    'description', 
    'summary',
    'environment'
)
issue_regexp = '^[a-zA-Z0-9]+-[\d]+$'
project_regexp = '^[a-zA-Z0-9]+$'


def initialize_jira():
    if ProjectSource.resource:
        return ProjectSource.resource    
    jira_url = __kupfer_settings__['jira_url']
    jira_login = __kupfer_settings__['jira_login']
    if jira_url and \
        jira_login and \
        jira_login.username and \
        jira_login.password:
        try:
            ProjectSource.resource = JIRA(jira_url,
                basic_auth=(
                    jira_login.username,
                    jira_login.password
                )
            )
        except:
            ProjectSource.resource = None
    return ProjectSource.resource


def get_issue(item, jira):
    if isinstance(item, issue):
        return item
    if isinstance(item.object, issue):
        return item.object
    key = None
    if re.match(issue_regexp, str(item)):
        key = str(item)
    elif re.match(issue_regexp, str(item.object)):
        key = str(item.object)
    if key:
        return jira.issue(key)
    

def get_issue_leaf(item, jira):
    if isinstance(item, IssueLeaf):
        return item
    i = get_issue(item, jira)
    return IssueLeaf(i, jira=jira)


def is_issue(item):
    if isinstance(item, issue):
        return item
    if isinstance(item.object, issue):
        return item.object
    if re.match(issue_regexp, str(item)):
        return True
    elif re.match(issue_regexp, str(item.object)):
        return True


def get_project(item, jira):
    if isinstance(item, project):
        return item
    if isinstance(item.object, project):
        return item.object
    key = None
    if re.match(project_regexp, str(item)):
        key = str(item)
    elif re.match(project_regexp, str(item.object)):
        key = str(item.object)
    if key:
        return jira.project(key)


def is_project(item):
    if isinstance(item, project):
        return item
    if isinstance(item.object, project):
        return item.object
    if re.match(project_regexp, str(item)):
        return True
    elif re.match(project_regexp, str(item.object)):
        return True


class IssueLeaf(Leaf):
    def __init__(self, obj, fields=None, transition=None, jira=None):
        Leaf.__init__(self, obj, obj.key)
        self.fields = fields
        self.transition = None
        self.jira = jira
    
    def get_description(self):
        return self.fields or self.object.fields.summary
    
    # def get_actions(self):
    #     valid_fields = []
    #     for field in self.object.raw['fields'].items():
    #         for show in FIELD_WHITE_LIST:
    #             if re.match(show, field[0]):
    #                 yield IssueChange(field, self.object, self.jira)
    #                 break


class ProjectLeaf(Leaf):
    def __init__(self, obj, jira):
        Leaf.__init__(self, obj, obj.key)
        self.jira = jira
    
    def get_description(self):
        return self.object.name


class ProjectSource(Source):
    resource = None
    def __init__(self):
        Source.__init__(self, "Jira Projects")
    
    def get_items(self):
        if ProjectSource.resource:
            for obj in ProjectSource.resource.projects():
                yield ProjectLeaf(obj, ProjectSource.resource)
    
    def initialize(self):
        ProjectSource.resource = initialize_jira()


class Jiraya(object):
    def __init__(self, jira=None):
        self._jira = jira
        
    @property
    def jira(self):
        self._jira = self._jira or initialize_jira()
        return self._jira

    @jira.setter
    def jira(self, value):
        self._jira = value


class Issue(Jiraya, Action):
    def __init__(self):
        Action.__init__(self, name="Jira Issue")
        Jiraya.__init__(self)
    
    def activate(self, item):
        return get_issue_leaf(item, self.jira)
    
    def item_types(self):
        yield TextLeaf
            
    def valid_for_item(self, item):
        return is_issue(item)
    
    def has_result(self):
        return True


class Show(Jiraya, Action):
    def __init__(self):
        Jiraya.__init__(self)
        Action.__init__(self, name="Show Issue/Project")
    
    def get_description(self):
        return "Open issue/project in browser"
    
    def activate(self, item):
        url = None
        if is_issue(item):
            i = get_issue(item, self.jira)
            url = i.permalink()
        else:
            p = get_project(item, self.jira)
            url = __kupfer_settings__['jira_url'] + \
                '/projects/' + p.key + '/summary'
        show_url(url)
    
    def valid_for_item(self, item):
        return is_issue(item) or is_project(item)
    
    def item_types(self):
        yield IssueLeaf
        yield ProjectLeaf
        yield TextLeaf


class Comment(Jiraya, Action):
    def __init__(self):
        Action.__init__(self, name="Add Comment")
        Jiraya.__init__(self)
            
    def valid_for_item(self, item):
        return is_issue(item)
    
    def item_types(self):
        yield IssueLeaf
        yield TextLeaf
    
    def activate(self, item, iobj):
        i = get_issue(item, self.jira)
        comment = self.jira.add_comment(i, iobj.object)
        return get_issue_leaf(item, self.jira)
            
    def valid_for_item(self, item):
        return is_issue(item)

    def requires_object(self):
        return True

    def object_types(self, for_item=None):
        yield TextLeaf

    def valid_object(self, iobj, for_item=None):
        return type(iobj) is TextLeaf
    
    def has_result(self):
        return True


class Assign(Jiraya, Action):
    def __init__(self):
        Action.__init__(self, name="Assign User")
        Jiraya.__init__(self)
            
    def valid_for_item(self, item):
        return is_issue(item)
    
    def item_types(self):
        yield IssueLeaf
        yield TextLeaf
    
    def activate(self, item, iobj):
        i = get_issue(item, self.jira)
        self.jira.assign_issue(i, iobj.object)
        return get_issue_leaf(item, self.jira)
            
    def valid_for_item(self, item):
        return is_issue(item)

    def requires_object(self):
        return True

    def object_types(self, for_item=None):
        yield TextLeaf

    def valid_object(self, iobj, for_item=None):
        return type(iobj) is TextLeaf
    
    def has_result(self):
        return True

    def object_source(self, for_item=None):
        if for_item:
            item = get_issue_leaf(for_item, self.jira)
            return _AssignValues(item)


class _AssignValues(Source, Jiraya):
    def __init__(self, issue):
        Source.__init__(self, _("Users"))
        Jiraya.__init__(self, issue.jira)
        self.issue = issue

    def get_items(self):
        i = get_issue(self.issue, self.jira)
        page_size = 50
        startAt = 0
        users = []
        while users or startAt == 0:
            users = self.jira.search_assignable_users_for_issues('',
                issueKey=i,
                startAt=startAt,
                maxResults=page_size)
            for u in users:
                yield TextLeaf(u.key, u.name)
            startAt = startAt + page_size

    def provides(self):
        yield TextLeaf


class ChangeStatus(Jiraya, Action):
    def __init__(self):
        Action.__init__(self, name="Change Status")
        Jiraya.__init__(self)
            
    def valid_for_item(self, item):
        return is_issue(item)
    
    def item_types(self):
        yield IssueLeaf
        yield TextLeaf
    
    def activate(self, item, iobj):
        i = get_issue(item, self.jira)
        l = get_issue_leaf(item, self.jira)
        self.jira.transition_issue(i, iobj.object, fields=l.fields)
        l.fields = None
        return l
            
    def valid_for_item(self, item):
        return is_issue(item)

    def requires_object(self):
        return True

    def object_types(self, for_item=None):
        yield TextLeaf

    def valid_object(self, iobj, for_item=None):
        return type(iobj) is TextLeaf
    
    def has_result(self):
        return True

    def object_source(self, for_item=None):
        if for_item:
            item = get_issue_leaf(for_item, self.jira)
            return _StatusValues(item)


class _StatusValues(Source, Jiraya):
    def __init__(self, issue):
        Source.__init__(self, _("Users"))
        Jiraya.__init__(self, issue.jira)
        self.issue = issue

    def get_items(self):
        i = get_issue(self.issue, self.jira)
        transitions = self.jira.transitions(i)
        for t in transitions:
            yield TextLeaf(t["id"], t["name"])

    def provides(self):
        yield TextLeaf


class SaveChanges(Jiraya, Action):
    def __init__(self):
        Action.__init__(self, name="Save issue changes")
        Jiraya.__init__(self)
    
    def item_types(self):
        yield IssueLeaf

    def valid_for_item(self, item):
        return item.fields or item.transition
    
    def get_description(self):
        return "Send changes to server"

    def activate(self, item):
        i = get_issue(item, self.jira)
        if item.transition:
            if item.fields:
                self.jira.transition_issue(i, item.transition, fields=item.fields)
            else:
                self.jira.transition_issue(i, item.transition)
        else:
            i.update(fields=item.fields)
        item.fields = None
        item.transition = None


class IssueChange(Jiraya, Action):
    def __init__(self, field, issue, jira):
        Action.__init__(self, name="Change " + field[0])
        Jiraya.__init__(self, jira)
        self.field = field
        self.issue = issue

    def requires_object(self):
        return True

    def activate(self, item, iobj):
        print(self.field, self.issue, self.jira, item, iobj)

    def valid_object(self, iobj, for_item=None):
        return type(iobj) is TextLeaf

    def object_source(self, for_item=None):
        return _IssueFieldValues(self.field, self.issue, self.jira)


class _IssueFieldValues(Source, Jiraya):
    def __init__(self, field, issue, jira):
        Source.__init__(self, _("Issue " + field[0] + " values"))
        Jiraya.__init__(self, jira)
        self.field = field
        self.issue = issue

    def get_items(self):
        return ()

    def provides(self):
        yield TextLeaf
        yield _IssueField


class _IssueField(Leaf, Jiraya):
    def __init__(self, obj, field, issue, jira):
        Leaf.__init__(self, obj, "Issue " + field[0] + " value " + obj)
        Jiraya.__init__(self, jira)
        self.field = field
        self.issue = issue
