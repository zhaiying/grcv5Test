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

class Plug_org_ztree(BaseField):
    '''普通部门选择框（单多选）
    '''
    f_type='org_ztree'
    f_open=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        
        #--相关按钮的默认值
        btns = {}
        btns['btn_ok']=''
        btns['btn_cancel']=''
        btns['btn_open']=''
        context = dict(btns,**context)
        if context['btn_open']=='self':
            context['btn_open']=element
        cfg= {} 
        cfg['tree_root']=element
        #cntr_scroll是ztree以外的卷滚容器，如果ztree展开后，恰好节点位于卷滚容器的显示区域外，则无法被点击，必须使卷滚容器的滚动条滚动，使节点显示出来才行，此参数存放对应的卷滚容器的css selector，该参数不存在，或值为空则不需要卷滚处理
        cfg['cntr_scroll']=''
        context = dict(cfg,**context)
        #--等待时间的默认值
        ws = {}
        #ws['quit_before'] = 0
        context = dict(ws,**context)
        
        if context['tree_root']=='':
            raise Exception('lack of parameters:tree_root')
            
        #与ztree原型不同，界面模型使用触发按钮作为element，需要转换一下
        el=Model_Standard_Ztree(uihandle,context['tree_root'],context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait_for_begin=self.getConfig('wait_for_begin',default=0.5,toType='float')
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
            
    def send(self,selections,context={}):
        
        sleep(self.wait_for_begin)
        
        self.open()
        
        #需要等待选择窗口加载完毕
        sleep(self.wait_for_begin)
        
        self.el.send(selections)
        self.ok()
        sleep(self.wait)

    
