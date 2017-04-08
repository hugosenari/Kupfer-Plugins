from .folks import FolksListener, it_folks, it_attrs, it_changes
from kupfer.objects import Source
from kupfer.obj import contacts
   

class FolksContact(contacts.ContactLeaf):
    def __init__(self, obj):
        self.folk = obj
        slots = {contacts.LABEL_KEY: obj.get_display_name()}
        for attr, key, value in it_attrs(obj):
            slots[attr] = slots.get(attr, {})
            slots[attr][key] = value
        email_addresses = slots.get('email_addresses', None)
        im_addresses = slots.get('im_addresses', None)
        if email_addresses:
            slots[contacts.EMAIL_KEY] = next(iter(email_addresses.values()))
        elif im_addresses:
            slots[contacts.EMAIL_KEY] = next(iter(im_addresses.values()))
        phone_numbers = slots.get('phone_numbers', None)
        if phone_numbers:
            slots[contacts.PHONE_KEY] = next(iter(phone_numbers.values()))
        contacts.ContactLeaf.__init__(self, slots, obj.get_display_name(), None)
    
    def get_description(self):
        email = self.object.get(contacts.EMAIL_KEY, '')
        phone = self.object.get(contacts.PHONE_KEY, '')
        return '{} {}'.format(email, phone)


class FolksSource(Source):
    def __init__(self):
        Source.__init__(self, _("Folks"))
        self.resource = None
        self.folks = {}
    
    def get_items(self):
        for contact in self.folks.values():
            yield contact
    
    def on_change(self, agg, changes):
        for old_folk, new_folk in it_changes(changes):
            if new_folk:
                self.folks[new_folk.get_id()] = FolksContact(new_folk)
            elif old_folk:
                del self.folks[old_folk.get_id()]
        self.mark_for_update()

    def on_ready(self, agg, *args):
        for folk in it_folks(agg):
            self.folks[folk.get_id()] = FolksContact(folk)
    
    def initialize(self):
        self.resource = FolksListener(self.on_ready, self.on_change)
        self.resource.initialize()
    
    def finalize(self):
        self.folks = {}
        self.resource = None

    def provides(self):
        yield FolksContact
