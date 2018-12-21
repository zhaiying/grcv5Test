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
# 包括 actions

class Plug_Ext_Actions(BaseField):
    '''扩展操作功能，用于处理相关扩展操作，例如编号、归档等，使用相同的接口调用field(ele,value,type,context)
    '''
    f_type='ext_actions'
    def __init__(self,uihandle,element='',page="", siteName="",context={}):
        self.handle=uihandle
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
        
    def send(self, actions='',context={}):
        #解析处理对系统变量的操作
        seperator = ';'
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
            '编号':self.number,
            '归档':self.archive
        }
        
        if switch.has_key(action):
            return switch[action](para,context)
        else:
            raise Exception('action %s is invalid!!!' % action)
    def number(self, v,context={}):
        values=self.parse(v)
        self.handle.field('下一步操作区','编号','btn_bar',context=context)
        for itm in values:
            if itm == '类别':
                self.handle.field('操作_编号_编号类型',values[itm],'select',context=context)
            elif itm == '值':
                self.handle.field('操作_编号_编号值',values[itm],'input',context=context)
        self.handle.field('弹出框_确定','','button',context=context)
    def archive(self, v,context={}):
        pass
        
        
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
 
    
