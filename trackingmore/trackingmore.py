## read plugin api:
## https://kupferlauncher.github.io/Documentation/PluginAPI.html
__kupfer_name__ = _('TrackingMore')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''Use trackingmore.com for package tracking'''
__kupfer_actions__ = ('PackageStatus', 'ViewPage')
__kupfer_sources__ = ('Curriers',)
  
from json import loads
from urllib import request, error
from kupfer.plugin_support import PluginSettings
from kupfer.objects import Action, Source, TextLeaf
from kupfer.utils import show_url

__kupfer_settings__ = PluginSettings( 
    {
        'key' : 'api_key',
        'label': _('API Key'),
        'type': str,
        'value': 'e1df6521-4f31-47ea-b4d1-d27799d495d2',
    }, 
)

CURRIERS_ENDPOINT = 'http://api.trackingmore.com/v2/carriers'
ENDPOINT = 'http://api.trackingmore.com/v2/trackings/{}/{}'
LINK = 'https://track.trackingmore.com/{}/en-{}.html'


def api_request(url):
    req = request.Request(
        url,
        headers={
            'Content-Type': 'application/json',
            'Trackingmore-Api-Key': __kupfer_settings__['api_key'],
            'Lang': 'en',
        }
    )
    with request.urlopen(req) as service:
        return loads(service.read())


class Currier(TextLeaf):
    def __init__(self, obj):
        TextLeaf.__init__(self, obj['code'], obj['name'])


class PackageStatusLeaf(TextLeaf):
    def __init__(self, obj, code, currier):
        self.code = code
        self.currier = currier
        txt = obj.get('meta', {}).get('message', '') 
        checkpoint = obj.get('data', {})
        if checkpoint:
            origin_info = checkpoint.get('origin_info', {})
            origin_info = origin_info if origin_info else {}
            trackinfos = origin_info.get('trackinfo', [])
            trackinfo = trackinfos[0] if trackinfos else {} 
            if trackinfo:
                fmt = '{StatusDescription} {Details} {Date}'
                txt = fmt.format(**trackinfo)
            else:
                fmt = '{status} {original_country} {updated_at}'
                txt = fmt.format(**checkpoint)
        TextLeaf.__init__(self, txt)


class Curriers(Source):
    def __init__(self):
        Source.__init__(self, 'TrackingMore Curriers')
    
    def produces(self):
        yield Currier
    
    def get_items(self):
        json = api_request(CURRIERS_ENDPOINT)
        curriers = json.get('data', [])
        for currier in curriers:
            yield Currier(currier)


class PackageStatus(Action):

    def __init__(self):
        Action.__init__(self, name=_('Package Status'))
  
    def activate(self, leaf, currier_leaf):
        url = ENDPOINT.format(currier_leaf.object, leaf.object)
        json = {}
        try:
            print(url)
            json = api_request(url)
        except error.HTTPError as err:
            json = {'meta':{'message': err.reason, 'code': err.code}}
        return PackageStatusLeaf(json, leaf.object, currier_leaf.object)
  
    def has_result(self):
        return True
    
    def item_types(self):
        yield TextLeaf

    def requires_object(self):
        return True

    def object_types(self, for_item=None):
        yield Currier


class ViewPage(Action):
    
    def __init__(self):
        Action.__init__(self, name=_('View at Trackingmore'))
  
    def activate(self, leaf):
        url = LINK.format(leaf.currier, leaf.code)
        show_url(url)

    def item_types(self):
        yield PackageStatusLeaf
