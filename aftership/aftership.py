## read plugin api:
## https://kupferlauncher.github.io/Documentation/PluginAPI.html
__kupfer_name__ = _('AfterShip')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''Uses AfterShip for package tracking'''
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
        'label': _('AfterShip Key'),
        'type': str,
        'value': '92139263-a1d7-40a4-847b-d82f536b51ea',
    }, 
)

CURRIERS_ENDPOINT = 'https://api.aftership.com/v4/couriers/all'
ENDPOINT = 'https://api.aftership.com/v4/last_checkpoint/{}/{}'
LINK = 'https://track.aftership.com/{}/{}'


def api_request(url):
    req = request.Request(
        url,
        headers={
            'Content-Type': 'application/json',
            'aftership-api-key': __kupfer_settings__['api_key']
        }
    )
    with request.urlopen(req) as service:
        return loads(service.read())


class Currier(TextLeaf):
    def __init__(self, obj):
        TextLeaf.__init__(self, obj['slug'], obj['name'])


class PackageStatusLeaf(TextLeaf):
    def __init__(self, obj, code, currier):
        self.obj = obj
        self.code = code
        self.currier = currier
        txt = self.obj.get('meta', {}).get('message', '') 
        checkpoint = self.obj.get('data', {}).get('checkpoint', {})
        if checkpoint:
            if checkpoint.get('message'):
                fmt = '{message} {country_name} {checkpoint_time}'
                txt = fmt.format(**checkpoint)
            else:
                txt = 'Empty status info'
        TextLeaf.__init__(self, txt)


class Curriers(Source):
    def __init__(self):
        Source.__init__(self, 'AfterShip Curriers')
    
    def produces(self):
        yield Currier
    
    def get_items(self):
        json = api_request(CURRIERS_ENDPOINT)
        curriers = json.get('data', {}).get('couriers', ())
        for currier in curriers:
            if not currier['required_fields']: 
                yield Currier(currier)


class PackageStatus(Action):

    def __init__(self):
        Action.__init__(self, name=_('Package Status'))
  
    def activate(self, leaf, currier_leaf):
        url = ENDPOINT.format(currier_leaf.object, leaf.object)
        json = {}
        try:
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
        Action.__init__(self, name=_('View at AfterShip'))
  
    def activate(self, leaf):
        url = LINK.format(leaf.currier, leaf.code)
        show_url(url)

    def item_types(self):
        yield PackageStatusLeaf
