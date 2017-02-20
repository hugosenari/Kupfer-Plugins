__kupfer_name__ = _("URL Encode")
__version__ = "0.1.1"
__author__ = "Hugo Sena Ribeiro <hugosenari@gmail.com>"
__description__ = _("""Decode and encode actions for kupfer""")
__kupfer_actions__ = ("URLEncode", "URLDecode")


import urllib
from kupfer.objects import Action, UrlLeaf, TextLeaf


class URLEncode(Action):
    def __init__(self):
        Action.__init__(self, name=_("URL Encode"))
    
    def activate(self, obj):
        result = ''
        try:
            result = urllib.quote(obj.object.encode('utf8'))
        except AttributeError:
            result = urllib.parse.quote(obj.object.encode('utf8'))
        return TextLeaf(result)
    
    def item_types(self):
        return UrlLeaf, TextLeaf
    
    def has_result(self):
        return True


class URLDecode(Action):
    def __init__(self):
        Action.__init__(self, name=_("URL Decode"))
    
    def activate(self, obj):
        result = ''
        try:
            result = urllib.unquote(obj.object)
        except AttributeError:
            result = urllib.parse.unquote(obj.object)
        return TextLeaf(result)
    
    def item_types(self):
        yield UrlLeaf
        yield TextLeaf
    
    def has_result(self):
        return True
