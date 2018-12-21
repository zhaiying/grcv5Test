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

from config import currentProject

#插件中不能使用innerload访问ext.models，因为models中引用了plugins.*，会产生循环调用，此处已经修改
# 界面测试组件维护在此--基本界面组件
# 包括 window

class Plug_Window(BaseField):
    '''视图功能
    '''
    f_type='window'
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        
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
            
            if v=='新窗口':
                v=''
            self.do(action,v,context)
            sleep(self.wait)
    def do(self,action,para,context):
        
        switch = {
            '切换到':self.switchWindow,
            '关闭后处理':self.closeWindow,
            '关闭':self.closeWindow,
            '关闭当前窗口':self.closeCurrentWindow
        }
        
        if switch.has_key(action):
            return switch[action](para,context)
        else:
            raise Exception('action %s is invalid!!!' % action)
    #切换到指定窗口
    def switchWindow(self, title,context={}):
        self.handle.switchWindow(title)
    #关闭指定窗口
    def closeCurrentWindow(self, title,context={}):
        #用于webdriver关闭当前窗体，并切换窗体控制权。一般用于测试的teardown返回初始状态
        self.handle.closeCurrentWindow(title)
    #返回上一窗体
    def closeWindow(self, title,context={}):
        #处理窗体由程序关闭，但控制权没有返回的情况
        
        self.handle.closeWindow(title)
    