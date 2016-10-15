#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from subprocess import call
from setuptools import setup
from setuptools.command.install import install
try:
    from configparser import ConfigParser  # @UnusedImport
except:
    from ConfigParser import ConfigParser  # @UnresolvedImport @Reimport

plugin_module = 'mpris_2'
plugin_path = path.dirname(path.abspath(__file__))


class CopyPlugin(install):

    def run(self):
        dirs = ["~", ".local", "share", "kupfer", "plugins"]
        install_path = path.expanduser(path.join(*dirs))
        print("mkdir {}".format(install_path))
        call("mkdir -p {}".format(install_path), shell=True)

        plugin_file = path.join(plugin_path, plugin_module + '.py')
        print("Copy {} to {}".format(plugin_file, install_path))
        call("cp -p {} {}".format(plugin_file, install_path), shell=True)

        plugin_file = path.join(plugin_path, plugin_module + '_plus.py')
        print("Copy {} to {}".format(plugin_file, install_path))
        call("cp -p {} {}".format(plugin_file, install_path), shell=True)
        
        print("Install dependency")
        call("pip install --user mpris2", shell=True)
        try:
            call("pip3 install --user mpris2", shell=True)
        except:
            pass
        try:
            call("pip2 install --user mpris2", shell=True)
        except:
            pass


def read_cfg():
    parser = ConfigParser()
    parser.read(path.join(plugin_path, 'setup.cfg'))
    for k, v in parser.items('metadata'):
        yield k, v

def convert(cfgs):
    from_to = {
        'summary': lambda k, v: ('description', v),
        'home-page': lambda k, v: ('url', v),
        'classifiers': lambda k, v: (k, v.splitlines()),
        'description-file': lambda k, v: ('long_description', open(v).read())
    }
    std_m = lambda k, v: (k.replace('-', '_'), v)
    for k, v in cfgs:
        m = from_to.get(k, std_m)
        yield m(k, v)

setup(
    cmdclass={'install': CopyPlugin},
    py_modules=[plugin_module, plugin_module + '_plus'],
    zip_safe=False,
    version='0.1.0',
    install_requires=['mpris2'],
    **dict(convert(read_cfg()))
)
