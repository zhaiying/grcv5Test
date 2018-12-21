#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-01-25 13:20
# plugings/__init__.py

__all__=['g_plugins','g_plugins_idx']

from glob import glob
from keyword import iskeyword
from os.path import dirname,join,split,splitext


#
#pdb.set_trace()

g_plugins={}
g_plugins_idx={}

basedir=dirname(__file__)

for name in glob(join(basedir, '*.py')):
    module = splitext(split(name)[-1])[0]
    if not module.startswith('_') and \
       not iskeyword(module):
        #print(__name__+'.'+module)
        __import__(__name__+'.'+module)
        m=globals()[module]
        props=dir(m)
        for i in range(0,len(props)):
            p=props[i]
            if(p.startswith("Plug_") or p.startswith('Model_')):
                o = getattr(m,p)
                __all__.append(p)
                g_plugins[p]=o
                g_plugins_idx[o.type()]=o
                globals()[p]=o
                
'''
def register_plugins(name):
    def _inner(func):
        g_plugins[name]=func
        return func
    return _inner
@register_plugins(name='hello')
def hello(a,b):
    print(a+b)
'''    
