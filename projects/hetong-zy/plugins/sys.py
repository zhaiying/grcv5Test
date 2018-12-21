#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-01-15 13:20
# plugins/sys.py

from log.log import Logger
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC

import re


from encapsulation.fields import BaseField
#pdb.set_trace()
from config import currentProject

#插件中不能使用innerload访问ext.models，因为models中引用了plugins.*，会产生循环调用，此处已经修改
# 界面测试组件维护在此--系统内部组件
# 包括 sys_var

class Plug_System_Var(BaseField):
    '''系统变量功能，用于设置、传递和销毁系统变量，例如正在处理的公文标题（该标题在处理过程中应一致,只能通过特定操作修改）
    '''
    f_type='sys_var'
    def __init__(self,uihandle,element='',page="", siteName="",context={}):
        self.handle=uihandle
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
        
    def send(self, actions='',context={}):
        #解析处理对系统变量的操作
        seperator = ','
        action_a = actions.split(seperator)
        for action in action_a:
            action = action.strip()
            pos = action.find('=')
            if pos>0:
                v=action[pos+1:]
                action=action[:pos]
            else:
                v=''
            
            self.do(action,v,context)
            sleep(self.wait)
    def do(self,action,para,context):
        
        switch = {
            '设置':self.set_var,
            '清除':self.remove_var
        }
        
        if switch.has_key(action):
            return switch[action](para,context)
        else:
            raise Exception('action %s is invalid!!!' % action)
    def set_var(self, v,context={}):
        values=self.parse(v)
        
        self.handle.set_context(values)
    def remove_var(self, v,context={}):
        self.handle.remove_context(v)
        
    #返回主窗体
    def backToDefault(self, title="",context={}):
        self.handle.driver.switch_to_default_content()
        
    def parse(self,v):
        #处理传入的参数键值对,每个键值对，用|区分键值，有逗号区分多个键值对。举例： flowDoc|发文$now[fmt:%Y%m%d]$,日期|2015-01-01
        values=v.split(',')
        ret_values={}
        for val in values:
            #解析键值
            pos = val.find('|')
            if pos>0:
                paraName = val[0:pos]
                paraValue = val[pos+1:]
                ret_values[paraName]=paraValue
        return ret_values
 
    
