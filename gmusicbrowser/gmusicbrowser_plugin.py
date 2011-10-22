from __future__ import absolute_import

__kupfer_name__ = _("gmusicbrowser")
__kupfer_sources__ = ("GmusicbrowserSource", )
__description__ = _("Control gmusicbrowser media player, It is based on the Exaile plugin. http://blog.stebalien.com/2010/04/kupfer-plugins.html")
__version__ = "0.1"
__author__ = "Hugo Ribeiro"

import dbus

from kupfer.objects import RunnableLeaf, Source
from kupfer.obj.apps import AppLeafContentMixin
from kupfer import utils, icons, pretty, uiutils

class PlayPause (RunnableLeaf):
	def __init__(self):
		RunnableLeaf.__init__(self, name=_("Play/Pause"))
	def run(self):
		utils.spawn_async(("gmusicbrowser", "-cmd", "PlayPause"))
	def get_description(self):
		return _("Resume/Pause playback in gmusicbrowser")
	def get_icon_name(self):
		return "media-playback-start"
class Next (RunnableLeaf):
	def __init__(self):
		RunnableLeaf.__init__(self, name=_("Next"))
	def run(self):
		utils.spawn_async(("gmusicbrowser", "-cmd", "NextSong"))
	def get_description(self):
		return _("Jump to next track in gmusicbrowser")
	def get_icon_name(self):
		return "media-skip-forward"

class Previous (RunnableLeaf):
	def __init__(self):
		RunnableLeaf.__init__(self, name=_("Previous"))
	def run(self):
		utils.spawn_async(("gmusicbrowser", "-cmd", "PrevSong"))
	def get_description(self):
		return _("Jump to previous track in gmusicbrowser")
	def get_icon_name(self):
		return "media-skip-backward"
class GmusicbrowserSource (AppLeafContentMixin, Source):
	appleaf_content_id = 'gmusicbrowser'
	def __init__(self):
		Source.__init__(self, _("gmusicbrowser"))
	def get_items(self):
		yield PlayPause()
		yield Next()
		yield Previous()
	def provides(self):
		yield RunnableLeaf
	def get_description(self):
		return __description__
	def get_icon_name(self):
		return "gmusicbrowser"
