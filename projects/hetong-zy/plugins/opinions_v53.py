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
#Model_LazyTree=currentProject.innerload('ext.models.Model_LazyTree')
#Model_Ulist=currentProject.innerload('ext.models.Model_Ulist')
from model import Model_Standard_Ztree

# 界面测试组件维护在此--基本界面组件
# 包括 org,cjs_org,fenfa_org,person,meeting_select,common_addressbook

class Plug_Opinion_v53(BaseField):
    '''普通部门选择框（单多选）
    '''
    f_type='opinion_v53'
    f_open=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        
        el=uihandle.element('',element,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def open(self):
        if(not self.f_open and self.el.btn_open!=''):
            self.el.open()
            self.f_open=True
        if(self.el.btn_open==''):
            self.f_open=True
    def ok(self):
        if(self.f_open and self.el.btn_ok!=''):
            self.el.ok()
            self.f_open=False
            sleep(self.wait)

    def cancel(self):
        if(self.f_open and self.el.btn_cancel!=''):
            self.el.cancel()
            self.f_open=False
            sleep(self.wait)
            
    def send(self,value,context={}):
        #触发意见对话框
        self.el.click()
        #输入意见
        self.handle.field('签署意见_意见框',value,type='input',context=context)
        #确定按钮
        self.handle.field('签署意见_意见按钮区','确定',type='btn_bar',context=context)
        #操作后延时
        sleep(self.wait)

    
