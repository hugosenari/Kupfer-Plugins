## read plugin api:
## https://kupferlauncher.github.io/Documentation/PluginAPI.html

__kupfer_name__ = _('Autocomplete')
__version__ = '0.1.0'
__author__ = 'Hugo Sena Ribeiro <hugosenari@gmail.com>'
__description__ = '''List shell autocomplete options'''
__kupfer_text_sources__ = ("ShellHistory",)
  
from kupfer.objects import TextLeaf
from kupfer.objects import TextSource
from kupfer import pretty
from subprocess import check_output
from itertools import zip_longest
from os import path


class ShellHistory(TextSource):
    def __init__(self):
        TextSource.__init__(self, _("Shell Story"))
    
    
    def get_text_items(self, text):
        return TextSource.get_text_items(self, text.encode())
    
    def get_items(self, text):
        if len(text) > 2:
            bash_it = self.ignore_error(self.bash_items, text)
            fish_it = self.ignore_error(self.fish_items, text)
            it = self.intercalate(bash_it, fish_it)
            for cmd in it:
                yield cmd
        raise StopIteration()
    
    def intercalate(self, it_a, it_b):
        for val_a, val_b in zip_longest(it_a, it_b):
            if val_a:
                yield val_a
            if val_b:
                yield val_b        
    
    def bash_items(self, text):
        bash_history_file = path.expanduser("~/.bash_history")
        mine = check_output(["file", "-i", bash_history_file])
        encoding = mine.split(b'=')[1].decode(errors="ignore")
        with open(bash_history_file, encoding=encoding) as history: 
            for command in history:
                if text in command.encode():
                    yield TextLeaf(command)
    
    def fish_items(self, text):
        history_cmd = "history search {}".format(text.decode(errors="ignore"))
        history = check_output(["fish", "-c", history_cmd]).split(b'\n')
        for command in history:
            if command:
                yield TextLeaf(command)
    
    def ignore_error(self, func, *args):
        it = ()
        try:
            it = func(*args)
        except StopIteration as e:
            return ()
        except Exception as e:
            pretty.print_error(__name__, type(e).__name__, e, func)
            return ()
        if not it:
            return ()
        while it:
            try:
                yield next(it)
            except StopIteration as e:
                raise e
            except Exception as e:
                pretty.print_error(__name__, type(e).__name__, e, func)
    
    def provides(self):
        yield TextLeaf
