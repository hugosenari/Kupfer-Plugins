__kupfer_name__ = _("Restart Apps")
__kupfer_sources__ = ()
__kupfer_actions__ = ("RestartApp", )
__description__ = _("""Restart applications.""")
__version__ = "0.1.1"
__author__ = "Hugo Sena Ribeiro <hugosenari gmail com>"

from kupfer import utils, launch, pretty
from kupfer.obj.base import Action
from kupfer.obj.objects import AppLeaf, CloseAll, Launch
from kupfer.plugin_support import PluginSettings

__kupfer_settings__ = PluginSettings( 
    {
        "key" : "app_end_timeout",
        "label": _("End timeout (sec)"),
        "type": int,
        "value": 10,
    },
    {
        "key" : "app_ended_interval",
        "label": _("Waiting end interval (sec)"),
        "type": int,
        "value": 1,
    },
)
  
#the actions
class RestartApp(Action):
    def __init__(self, leaf=None, retry = 0):
        Action.__init__(self, _("Restart aplication"))
        self.retry = retry
        if leaf != None:
            self.activate(leaf)
    
    def item_types(self):
        yield AppLeaf

    def get_description(self):
        return _("Restart this")
    
    def valid_for_item(self, leaf):
        return launch.application_is_running(leaf.get_id())
    
    def activate(self, leaf):
        closer = CloseAll()
        if closer.valid_for_item(leaf): closer.activate(leaf)
        if (not launch.application_is_running(leaf.get_id())):
            pretty.print_debug(__name__, 'App stoped')
            launcher = Launch()
            if launcher.valid_for_item(leaf): launcher.activate(leaf, self.wants_context())
        else:
            pretty.print_debug(__name__, 'App not ended yet')
            interval = utils.parse_time_interval("%ss" % (__kupfer_settings__["app_ended_interval"]))
            self.retry+=1
            if self.try_again(self.retry):
                pretty.print_debug(__name__, 'App not ended yet - retry')
                from kupfer import scheduler
                timer = scheduler.Timer(True)
                timer.set(interval, RestartApp, leaf, self.retry)
            else:
                pretty.print_debug(__name__, 'App will not end - abort')

    def try_again(self, retry):
        app_ended_interval = __kupfer_settings__["app_ended_interval"]
        app_end_timeout = __kupfer_settings__["app_end_timeout"]
        max_run_times = app_end_timeout/app_ended_interval
        pretty.print_debug(__name__, 'app_ended_interval %s, app_end_timeout %s, retry %s, max_run_times %s' %(app_ended_interval, app_end_timeout, retry , max_run_times))
        return retry <= max_run_times - 1
