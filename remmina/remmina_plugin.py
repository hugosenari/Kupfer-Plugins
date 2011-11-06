# -*- coding: UTF-8 -*-
__author__ = u"Hugo Sena Ribeiro <hugosenari gmail com>"
__description__ = _("""Start remmina sessions""")
__kupfer_actions__ = (u"RemminaConnect",)
__kupfer_name__ = _(u"Remmina")
__kupfer_sources__ = (u"ReminaHostServiceSource",)
__version__ = "1.1"

from kupfer import pretty, utils
from kupfer.obj.apps import AppLeafContentMixin
from kupfer.objects import Action
from kupfer.obj.grouping import ToplevelGroupingSource
from kupfer.obj.helplib import FilesystemWatchMixin
from kupfer.obj.hosts import HostLeaf, HostServiceLeaf, HOST_ADDRESS_KEY,\
	HOST_NAME_KEY, HOST_SERVICE_NAME_KEY, HOST_SERVICE_PASS_KEY,\
	HOST_SERVICE_PORT_KEY, HOST_SERVICE_REMOTE_PATH_KEY,\
	HOST_SERVICE_USER_KEY
from kupfer.plugin_support import PluginSettings
import fnmatch
import os
import re
import tempfile


__kupfer_settings__ = PluginSettings( 
        {
                "key" : "remmina_config_folder",
                "label": _("Remina config folder"),
                "type": str,
                "value": os.path.join(
                                (os.getenv('USERPROFILE') or os.getenv('HOME')),
                                '.remmina'),
        }
)

class ReminnaHostServiceLeaf(HostServiceLeaf):
	def __init__(self, item):
		HostServiceLeaf.__init__(self, item.get('name'),
					 item.get('server')
					        or item.get('ssh_server'),
					 item.get('protocol'),
					 item.get('description'),
					 item.get('port'),
					 item.get('username')
					        or item.get('ssh_username'),
					 item.get('password')
					        or item.get('ssh_password'),
					 item)
	def get_icon_name(self):
		return "network-server"

class ReminaHostServiceSource(AppLeafContentMixin, ToplevelGroupingSource,
			      FilesystemWatchMixin):
	'''Remmina leaf factory'''
	appleaf_content_id = 'remmina'
	def __init__(self, name=_("Remmina Hosts")):
		ToplevelGroupingSource.__init__(self, name, _("Remmina"))
		source_user_reloadable = True
		self._remina_home = __kupfer_settings__["remmina_config_folder"]

	def initialize(self):
		ToplevelGroupingSource.initialize(self)
		self.monitor_token = self.monitor_directories(self._remina_home)	

	def provides(self):
		yield ReminaHostServiceSource

	def get_description(self):
		return __description__

	def get_icon_name(self):
		return "remmina"

	def get_items(self):
		try:
			for file in os.listdir(self._remina_home):
				try:
					uri = os.path.join(self._remina_home, file)
					if fnmatch.fnmatch(file, '*.remmina'):
						yield self.parse_file(uri)
				except Exception, exc:
					pretty.print_error(
						__name__,
						type(exc).__name__,
						exc)
		except Exception, exc:
			pretty.print_error(
				__name__,
				type(exc).__name__,
				exc)

	def parse_file(self, uri):
		return ReminnaHostServiceLeaf(
			ReminaHostServiceSource._parse_file(uri))

	@staticmethod
	def _parse_file(uri):
		file = None
		result = {'path': uri}
		file = open(uri)
		reg = re.compile("([^=]+)=(.+)")
		for line in file.readlines():
			match = reg.match(line)
			if match:
				key, value = match.groups()
				key = key.strip()
				valeu = value.strip()
				result[key] = value
		file.close()
		result['description'] = "%s : %s : %s : %s" % (
			result.get('group'),
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
		yield HostLeaf
		yield HostServiceLeaf
		yield ReminnaHostServiceLeaf

	def valid_for_item(self, leaf):
		"""Whether action can be used with exactly @item"""
		return leaf.check_key('path')\
			or leaf.check_key('TSCLIENT_SESSION')\
			#or isinstance(leaf, HostServiceLeaf)

	def activate(self, leaf):
		obj = leaf.object
		if obj.get('path') or obj.get('TSCLIENT_SESSION'):
			utils.spawn_async(("remmina", "-c",
				obj.get('path') or obj.get('TSCLIENT_SESSION')))
	#
	#	elif isinstance(leaf, HostServiceLeaf):
	#		(path, file) = utils.get_safe_tempfile()
	#		tmp = open(os.path.join(path, file), 'r+')
	#		tmp.seek(0)
	#		tmp.write('\n[remmina]\n')
	#		obj = RemminaConnect.remminize(obj)
	#		for key in obj:
	#			value = obj[key] if obj[key] else ''
	#			tmp.write("\n%s=%s" % (key, value))
	#		tmp.flush()
	#		tmp.close()
	#		pretty.print_debug(__name__, tmp.name)
	#		utils.spawn_async(("remmina", "-c", tmp.name))
	#		utils.spawn_async(("cat", tmp.name))
	#
	#@staticmethod
	#def remminize(obj):
	#	result = {
	#		'name': obj.get(HOST_NAME_KEY),
	#		'password': obj.get(HOST_SERVICE_PASS_KEY),
	#		'path': obj.get(HOST_SERVICE_REMOTE_PATH_KEY),
	#		'port': obj.get(HOST_SERVICE_PORT_KEY),
	#		'protocol': obj.get(HOST_SERVICE_NAME_KEY),
	#	}
	#	result.update(obj)
	#	if result['port'] == '22' or re.match(
	#		'([Ss][Ff][Tt][Pp])|([Ss]{2}[Hh])', result['protocol']):
	#		result['ssh_enabled'] = 1
	#		result['ssh_server'] = obj.get(HOST_ADDRESS_KEY)
	#		result['ssh_username'] = obj.get(HOST_SERVICE_USER_KEY)
	#	else:
	#		result['server'] = obj.get(HOST_ADDRESS_KEY)
	#		result['username'] = obj.get(HOST_SERVICE_USER_KEY)
	#	result.update(obj)
	#	return result