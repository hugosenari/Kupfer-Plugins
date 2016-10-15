"""Create QRCodes from texts or urls. Useful for smartphones with QRCode
readers: Create some url with kupfer and QRCode it. Get it with the phone and 
use it's browser to display"""

__kupfer_name__ = _("Show QRCode")
__kupfer_actions__ = (
            "ShowQRCode",
    )
__description__ = _("Display text as QRCode in a window")
__version__ = "0.1.0"
__author__ = "Thomas Renard <cybaer42@web.de>"

import StringIO

import gtk
import qrencode

from kupfer.objects import Action, Leaf
from kupfer.obj.contacts import email_from_leaf


class ShowQRCode (Action):
    """Create QRCode windows from text or url"""

    def __init__(self):
        """initialize action"""
        Action.__init__(self, _("Show QRCode"))

    def wants_context(self):
        return True

    def activate(self, leaf, ctx):
        """Create the image from leaf text and display it on window"""
        text = qrcode_txt(leaf)
        img = qrcode_img(text)
        window = img_viewer(img)
        ctx.environment.present_window(window)

    def item_types(self):
        yield Leaf

    def valid_for_item(self, leaf):
        return hasattr(leaf, "get_text_representation")\
            or hasattr(leaf, "qrcode")

    def get_description(self):
        """The Action description"""
        return _("Display text as QRCode in a window")

    def get_icon_name(self):
        """Name of the icon"""
        return "format-text-bold"


PROTOCOLS = {
    "qrcode": lambda l: l.qrcode(),
    "IMContact": lambda l: l.repr_key(),
    "email": lambda l: email_from_leaf(l),
    "text": lambda l: l.get_text_representation(),
    "phone": lambda l: "tel:%s" % l.object.get("PHONE"),
    "mecard": lambda l: "MECARD:N:%s;ADR:%s;TEL:%s;EMAIL:%s;;" % (
        l.object.get("NAME",""), l.object.get("ADDRESS",""),
        l.object.get("PHONE",""),l.object.get("EMAIL","")
    )
}

def qrcode_type(leaf):
    if hasattr(leaf, "qrcode"):
        return "qrcode"

    o = leaf.object
    if hasattr(o, "get"):
        if o.get("NAME") and (o.get("ADDRESS")
                              or o.get("PHONE")
                              or o.get("EMAIL")):
            return "mecard"
        if "PHONE" in o:
            return "phone"

    if hasattr(leaf, "im_id_kind"):
        return "IMContact"

    if bool(email_from_leaf(leaf)):
        return "email"

    return "text"

def qrcode_txt(leaf):
    key = qrcode_type(leaf)
    trasnlator = PROTOCOLS[key]
    return trasnlator(leaf)

def qrcode_img(text):
    image_file = StringIO.StringIO()
    image = qrencode.encode_scaled(text, size=300)[2]
    image.save(image_file, "ppm")
    image_contents = image_file.getvalue()
    image_file.close()
    return image_contents

def img_viewer(image_contents):
    loader = gtk.gdk.PixbufLoader("pnm")
    loader.write(image_contents, len(image_contents))
    pixbuf = loader.get_pixbuf()
    loader.close()
    window = gtk.Window()
    window.set_default_size(350, 350)
    image = gtk.Image()
    image.set_from_pixbuf(pixbuf)
    image.show()
    window.add(image)
    return window
