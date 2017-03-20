# -*- coding: UTF-8 -*-
# vim: set noexpandtab ts=8 sw=8:
__kupfer_name__ = _("Empathetic")
__kupfer_sources__ = ("ContactsSource", )
__kupfer_actions__ = ("ChangeStatus", 'OpenChat')
__description__ = _("Access to Empathy Contacts")
__version__ = "0.1.2"
__author__ = "Jakh Daven <tuxcanfly@gmail.com>"

import dbus
import time

from kupfer import icons
from kupfer import plugin_support
from kupfer import pretty
from kupfer.objects import Leaf, Action, Source, AppLeaf
from kupfer.weaklib import dbus_signal_connect_weakly
from kupfer.obj.helplib import PicklingHelperMixin
from kupfer.obj.apps import AppLeafContentMixin
from kupfer.obj.grouping import ToplevelGroupingSource
from kupfer.obj.contacts import ContactLeaf, JabberContact, JABBER_JID_KEY

__kupfer_settings__ = plugin_support.PluginSettings(
    {
        "key" : "show_offline",
        "label": _("Show offline contacts"),
        "type": bool,
        "value": False,
    },
)

plugin_support.check_dbus_connection()

_STATUSES = {
    'available': _('Available'),
    'away':      _('Away'),
    'dnd':       _('Busy'),
    'xa':        _('Not Available'),
    'hidden':    _('Invisible'),
    'offline':   _('Offline')
}

_ATTRIBUTES = {
    'alias':          'org.freedesktop.Telepathy.Connection.Interface.Aliasing/alias',
    'presence':       'org.freedesktop.Telepathy.Connection.Interface.SimplePresence/presence',
    'contact_caps':   'org.freedesktop.Telepathy.Connection.Interface.ContactCapabilities.DRAFT/caps',
    'jid':            'org.freedesktop.Telepathy.Connection/contact-id',
    'caps':           'org.freedesktop.Telepathy.Connection.Interface.Capabilities/caps',
}


ACCOUNTMANAGER_PATH      = "/org/freedesktop/Telepathy/AccountManager"
ACCOUNTMANAGER_IFACE     = "org.freedesktop.Telepathy.AccountManager"
ACCOUNT_IFACE            = "org.freedesktop.Telepathy.Account"
CHANNEL_GROUP_IFACE      = "org.freedesktop.Telepathy.Channel.Interface.Group"
CONTACT_IFACE            = "org.freedesktop.Telepathy.Connection.Interface.Contacts"
SIMPLE_PRESENCE_IFACE    = "org.freedesktop.Telepathy.Connection.Interface.SimplePresence"
DBUS_PROPS_IFACE         = "org.freedesktop.DBus.Properties"
CHANNELDISPATCHER_IFACE  = "org.freedesktop.Telepathy.ChannelDispatcher"
CHANNELDISPATCHER_PATH   = "/org/freedesktop/Telepathy/ChannelDispatcher"
CHANNEL_TYPE             = "org.freedesktop.Telepathy.Channel.ChannelType"
CHANNEL_TYPE_TEXT        = "org.freedesktop.Telepathy.Channel.Type.Text"
CHANNEL_TARGETHANDLE     = "org.freedesktop.Telepathy.Channel.TargetHandle"
CHANNEL_TARGETHANDLETYPE = "org.freedesktop.Telepathy.Channel.TargetHandleType"
EMPATHY_CLIENT_IFACE     = "org.freedesktop.Telepathy.Client.Empathy"

EMPATHY_ACCOUNT_KEY = "EMPATHY_ACCOUNT"
EMPATHY_CONTACT_ID  = "EMPATHY_CONTACT_ID"

def _create_dbus_connection():
    try:
        sbus = dbus.SessionBus()
        proxy_obj = sbus.get_object(ACCOUNTMANAGER_IFACE, ACCOUNTMANAGER_PATH)
        dbus_iface = dbus.Interface(proxy_obj, DBUS_PROPS_IFACE)
        return dbus_iface
    except dbus.DBusException as exc:
        pretty.print_error(__name__, type(exc).__name__, exc)


class EmpathyContact(JabberContact):

    def __init__(self, jid, name, status, resources, account, contact_id):
        empathy_slots= { EMPATHY_ACCOUNT_KEY: account, EMPATHY_CONTACT_ID: contact_id }
        JabberContact.__init__(self, jid, name, status, resources, empathy_slots)

    def repr_key(self):
        return "".join((self.object[JABBER_JID_KEY], self.object[EMPATHY_ACCOUNT_KEY]))

    def get_gicon(self):
        return icons.ComposedIconSmall(self.get_icon_name(), "empathy")
    
    def __cmp__(self, o):
        return type(o) == EmpathyContact and self.repr_key() == o.repr_key()


class AccountStatus(Leaf):
    pass


class OpenChat(Action):

    def __init__(self):
        Action.__init__(self, _('Open Chat'))

    def activate(self, leaf):
        bus = dbus.SessionBus()
        jid = JABBER_JID_KEY in leaf and leaf[JABBER_JID_KEY]
        account = bus.get_object(ACCOUNTMANAGER_IFACE, leaf[EMPATHY_ACCOUNT_KEY])
        contact_id = leaf[EMPATHY_CONTACT_ID]

        channel_dispatcher_iface = bus.get_object(CHANNELDISPATCHER_IFACE, CHANNELDISPATCHER_PATH)
        ticks = dbus.Int64(time.time())
        channel_request_params = dbus.Dictionary()
        channel_request_params[CHANNEL_TYPE] = dbus.String(CHANNEL_TYPE_TEXT, variant_level=1)
        channel_request_params[CHANNEL_TARGETHANDLETYPE] = dbus.UInt32(1, variant_level=1)
        channel_request_params[CHANNEL_TARGETHANDLE] = contact_id
        message_channel_path = channel_dispatcher_iface.EnsureChannel(account, channel_request_params, ticks, EMPATHY_CLIENT_IFACE)
        channel_request = bus.get_object(ACCOUNTMANAGER_IFACE, message_channel_path)
        channel_request.Proceed()


    def get_icon_name(self):
        return 'empathy'

    def item_types(self):
        yield ContactLeaf

    def valid_for_item(self, item):
        return EMPATHY_ACCOUNT_KEY in item and item[EMPATHY_ACCOUNT_KEY]


class ChangeStatus(Action):
    ''' Change global status '''

    def __init__(self):
        Action.__init__(self, _('Change Global Status To...'))

    def activate(self, leaf, iobj):
        bus = dbus.SessionBus()
        interface = _create_dbus_connection()
        for valid_account in interface.Get(ACCOUNTMANAGER_IFACE, "ValidAccounts"):
            #ignore fails by account
            try:
                account = bus.get_object(ACCOUNTMANAGER_IFACE, valid_account)
                connection_status = account.Get(ACCOUNT_IFACE, "ConnectionStatus")
                if connection_status != 0:
                    continue
    
                if iobj.object == "offline":
                    false = dbus.Boolean(0, variant_level=1)
                    account.Set(ACCOUNT_IFACE, "Enabled", false)
                else:
                    connection_path = account.Get(ACCOUNT_IFACE, "Connection")
                    connection_iface = connection_path.replace("/", ".")[1:]
                    connection = bus.get_object(connection_iface, connection_path)
                    simple_presence = dbus.Interface(connection, SIMPLE_PRESENCE_IFACE)
                    simple_presence.SetPresence(iobj.object, _STATUSES.get(iobj.object))
            except dbus.DBusException as exc:
                pretty.print_error(__name__, type(exc).__name__, exc)

    def item_types(self):
        yield AppLeaf

    def valid_for_item(self, leaf):
        return leaf.get_id() == 'empathy'

    def requires_object(self):
        return True

    def object_types(self):
        yield AccountStatus

    def object_source(self, for_item=None):
        return StatusSource()


class ContactsSource(AppLeafContentMixin, ToplevelGroupingSource,
        PicklingHelperMixin):
    ''' Get contacts from all on-line accounts in Empathy via DBus '''
    appleaf_content_id = 'empathy'

    def __init__(self, name=_('Empathy Contacts')):
        super(ContactsSource, self).__init__(name, "Contacts")
        self._version = 3
        self.unpickle_finish()

    def pickle_prepare(self):
        self._contacts = []

    def unpickle_finish(self):
        self.mark_for_update()
        self._contacts = []

    def initialize(self):
        ToplevelGroupingSource.initialize(self)

    def get_items(self):
        interface = _create_dbus_connection()
        if interface is not None:
            self._find_all_contacts(interface)
            
        if self._contacts is not None:
            return self._contacts
        return []

    def _find_all_contacts(self, interface):
        bus = dbus.SessionBus()
        for valid_account in interface.Get(ACCOUNTMANAGER_IFACE, "ValidAccounts"):
            try: #ignore account errors
                account = bus.get_object(ACCOUNTMANAGER_IFACE, valid_account)
                connection_status = account.Get(ACCOUNT_IFACE, "ConnectionStatus")
                if connection_status != 0:
                    continue

                connection_path = account.Get(ACCOUNT_IFACE, "Connection")
                connection_iface = connection_path.replace("/", ".")[1:]
                connection = bus.get_object(connection_iface, connection_path)
                connection.ListChannels(
                    reply_handler=lambda *args, **kwds:
                        self._reply_handle_channels({
                            'connection':connection,
                            'connection_iface':connection_iface,
                            'bus':bus,
                            'valid_account':valid_account}, *args, **kwds),
                    error_handler=lambda *args, **kwds:
                        self._error_handle_channels(*args, **kwds),)
            except dbus.DBusException as exc:
                pretty.print_error(__name__, type(exc).__name__, exc)
    
    def _reply_handle_channels(self, opts, channels, *args, **kwds):
        show_offline = __kupfer_settings__["show_offline"]
        csize = len(self._contacts)
        for channel in channels:
            try: #ignore channel errors
                contact_group = opts['bus'].get_object(opts['connection_iface'], channel[0])
                contacts = None
                
                if str(contact_group).find('ImChannel') < 0:
                    contacts = contact_group.Get(CHANNEL_GROUP_IFACE, "Members")
                if contacts:
                    contacts = [c for c in contacts]
                    contact_attributes = opts['connection'].Get(CONTACT_IFACE, "ContactAttributeInterfaces")
                    contact_attributes = [str(a) for a in contact_attributes]            
                    contact_details = opts['connection'].GetContactAttributes(contacts, contact_attributes, False)
                    for contact, details in contact_details.items():
                        try: #ignore contact errors
                            status_code = details.get(
                                _ATTRIBUTES.get("presence"),
                                [None , 'offline']
                            )[1]
                            if not show_offline and status_code == 'offline':
                                continue
                            empathyContact = EmpathyContact(
                                details[_ATTRIBUTES.get("jid")],
                                details[_ATTRIBUTES.get("alias")],
                                _STATUSES.get(status_code),
                                '', # empathy does not provide resource here AFAIK
                                opts['valid_account'],
                                contact)
                            if empathyContact in self._contacts:
                                self._contacts[self._contacts.index(empathyContact)] = empathyContact
                            else:
                                self._contacts.append(empathyContact)
                            
                        except dbus.DBusException as exc:
                            pretty.print_error(__name__, type(exc).__name__, exc)
            except dbus.DBusException as exc:
                pretty.print_error(__name__, type(exc).__name__, exc)
        if csize == self._contacts:
            return None
        self.mark_for_update()

    def _error_handle_channels(self, *args, **kwds):
        pretty.print_error(__name__, *args, **kwds)

    def get_icon_name(self):
        return 'empathy'

    def provides(self):
        yield ContactLeaf


class StatusSource(Source):

    def __init__(self):
        Source.__init__(self, _("Empathy Account Status"))

    def get_items(self):
        for status, name in _STATUSES.items():
            yield AccountStatus(status, name)

    def provides(self):
        yield AccountStatus

