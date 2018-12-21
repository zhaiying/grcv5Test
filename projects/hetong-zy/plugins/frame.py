#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-01-15 13:20
# plugins/addressbook.py

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
# 界面测试组件维护在此--基本界面组件
# 包括 frame

class Plug_Frame(BaseField):
    '''视图功能
    '''
    f_type='frame'
    def __init__(self,uihandle,element='',page="", siteName="",context={}):
        self.handle=uihandle
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
        
    def send(self, actions='',context={}):
        #解析处理对视图的操作
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
            '切换到':self.switchTo,
            '返回':self.backToDefault
        }
        
        if switch.has_key(action):
            return switch[action](para,context)
        else:
            raise Exception('action %s is invalid!!!' % action)
    #切换到指定帧
    def switchTo(self, title,context={}):
        utsframe = self.handle.element('',title)
        self.handle.driver.switch_to_frame(utsframe)
        
    #返回主窗体
    def backToDefault(self, title="",context={}):
        self.handle.driver.switch_to_default_content()
        

    
