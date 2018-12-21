#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys 

class SysContext(object):
    #用于处理多个用例之间的协调
    global_context={}
    handle_context={}
    session_context={}
    handle = None
    
    def __init__(self):
        self.handle_cmd_args()
        
    def handle_cmd_args(self):
        #处理命令行传参，当做系统参数(非-开头的，有=的是我们的保留参数)
        left_args=sys.argv[0:1]
        for i in range(1, len(sys.argv)): 
            val = sys.argv[i]
            pos = val.find('=')
            
            if val.startswith('-') or pos<=0:
                # -或--开头或不包含=，是unittest的保留参数，忽略等待unittest后续处理
                left_args.append(val)
                
            else:
                #保留参数
                paraName = val[0:pos]
                paraValue = val[pos+1:]
                self.global_context[paraName] = paraValue
        #将过滤后的参数重新传递给后续的处理程序，例如unittest
        sys.argv = left_args    
            
    def get_raw_context(self,scope=''):
        scope = scope.strip().lower()
        if scope == 'global':
            #global context
            context = self.global_context
        elif scope == 'handle':
            #handle context
            context = dict(self.global_context,**(self.handle_context))
        else:
            #默认是获取session context
            context = dict(self.global_context,**(self.handle_context))
            context = dict(context,**(self.session_context))
        return context
    def get_raw(self,name,default='',scope=''):
        context = self.get_raw_context(scope)
        if context.has_key(name):
            return context[name]
        else:
            return default
