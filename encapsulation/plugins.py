
__all__=['smartPlugin']



from config import currentProject
__module=currentProject.innerload('plugins')
__all=__module.__all__

for _i in range(0,len(__module.__all__)):
    _p=__all[_i]
    _plugin=getattr(__module,_p)
    globals()[_p]=_plugin
    __all__.append(_p)

def smartPlugin(typename):
    if(g_plugins_idx.has_key(typename)):
        plugin=g_plugins_idx[typename]
        return plugin
    
