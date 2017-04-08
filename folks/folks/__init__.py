## read plugin api:
## https://kupferlauncher.github.io/Documentation/PluginAPI.html
_ = lambda x: x
__kupfer_name__ = _('Folks (Contacts)')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''List contacts using libfolks as source'''
__kupfer_sources__ = ("FolksSource",)

try:
    from .plugin import FolksSource
except:
    pass