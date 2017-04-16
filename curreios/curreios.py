
## read plugin api:
## https://kupferlauncher.github.io/Documentation/PluginAPI.html

__kupfer_name__ = _('Curreios')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''Realiza rastreio de seu pacote nos correios'''
__kupfer_actions__ = ("ShowTrackPage", "LastStatus")


import re
from urllib import request
from kupfer.utils import show_url
from kupfer.objects import TextLeaf
from kupfer.objects import Action

CORREIOS_URL = "http://websro.correios.com.br/sro_bin/txect01$.QueryList?{}"
CORREIOS_PARAMS = "P_LINGUA=001&P_TIPO=001&P_COD_UNI={}"


def to_correios_url(leaf):
    query = CORREIOS_PARAMS.format(leaf.object)
    url = CORREIOS_URL.format(query)
    return url


class ShowTrackPage(Action):

    def __init__(self):
        Action.__init__(self, name=_("Ver nos correios"))

    def activate(self, leaf):
        show_url(to_correios_url(leaf))

    def item_types(self):
        yield TextLeaf


def get_tracking_info(content):
    result = []
    #filter lines
    trs = (l.strip('<tr><td') 
        for l in content.split('\n') 
            if l.startswith('<tr><td'))
    
    # fill content
    for line in trs:
        cols = line.split('<td')
        r = []
        for col in cols:
            match = re.match(".*>([^<]+)<", col)
            if match:
                r.append(match.group(1))

        if len(cols) == 1 and result:
            result[-1] = result[-1] + r
        else:
            result.append(r)
    return result


class LastStatus(Action):

    def __init__(self):
        Action.__init__(self, name=_("Ultimo status"))

    def activate(self, leaf):
        url = to_correios_url(leaf)
        with request.urlopen(url) as curreio:
            content = curreio.read()
            info = get_tracking_info(content.decode('iso-8859-1'))
            if info:
                txt = '-'.join(reversed(info[0]))
                return TextLeaf(txt, leaf.object)

    def item_types(self):
        yield TextLeaf

    def has_result(self):
        return True
