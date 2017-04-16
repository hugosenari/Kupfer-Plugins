## read plugin api:
## https://kupferlauncher.github.io/Documentation/PluginAPI.html
_ = lambda x: x
__kupfer_name__ = _('AfterShip')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''Uses AfterShip for package tracking'''
__kupfer_actions__ = ('PackageStatus',)
__kupfer_sources__ = ('AfterShipCurriers',)
  
from json import loads
from urllib import request, error
from kupfer.plugin_support import PluginSettings
from kupfer.objects import Action, Source, TextLeaf

__kupfer_settings__ = PluginSettings( 
    {
        'key' : 'aftership_key',
        'label': _('AfterShip Key'),
        'type': str,
        'value': '92139263-a1d7-40a4-847b-d82f536b51ea',
    }, 
)

CURRIERS_ENDPOINT = 'https://api.aftership.com/v4/couriers/all'
ENDPOINT = 'https://api.aftership.com/v4/last_checkpoint/{}/{}'


def aftership_request(url):
    req = request.Request(
        url,
        headers={
            'Content-Type': 'application/json',
            'aftership-api-key': __kupfer_settings__['aftership_key']
        }
    )
    with request.urlopen(req) as service:
        return loads(service.read())


class AfterShipCurrier(TextLeaf):
    def __init__(self, obj):
        TextLeaf.__init__(self, obj['slug'], obj['name'])


class AfterShipCurriers(Source):
    def __init__(self):
        Source.__init__(self, 'AfterShip Curriers')
    
    def produces(self):
        yield AfterShipCurrier
    
    def get_items(self):
        json = aftership_request(CURRIERS_ENDPOINT)
        curriers = json.get('data', {}).get('couriers', ())
        for currier in curriers:
            if not currier['required_fields']: 
                yield AfterShipCurrier(currier)


class PackageStatus(Action):

    def __init__(self):
        Action.__init__(self, name=_('Package Status'))
  
    def activate(self, leaf, currier_leaf):
        url = ENDPOINT.format(currier_leaf.object, leaf.object)
        json = {}
        try:
            json = aftership_request(url)
        except error.HTTPError as err:
            json = {'meta':{'message': err.reason, 'code': err.code}}
        txt = json.get('meta', {}).get('message', '') 
        checkpoint = json.get('data', {}).get('checkpoint', {})
        if checkpoint:
            if checkpoint.get('message'):
                fmt = '{message} {country_name} {checkpoint_time}'
                txt = fmt.format(**checkpoint)
            else:
                txt = 'Empty status info'
        return TextLeaf(leaf.object, txt)
  
    def has_result(self):
        return True
    
    def item_types(self):
        yield TextLeaf

    def requires_object(self):
        return True

    def object_types(self, for_item=None):
        yield AfterShipCurrier


if __name__ == '__main__':
    json = aftership_request(CURRIERS_ENDPOINT)
    print(json)