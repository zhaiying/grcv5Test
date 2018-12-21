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
from model import Model_table
#from encapsulation.plugins import smartPlugin
from base import Plug_btn_bar
# 界面测试组件维护在此--基本界面组件
# 包括 view_panel

class Plug_View_Panel(BaseField):
    '''视图功能
    '''
    f_type='view_panel'
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        
        self.handle=uihandle
        #内置视图对象，作为相关功能入口
        el=Model_table(uihandle,element,context=context,parent=self)
        self.view_body=el
        self.el=el
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
        self.max_page=self.getConfig('max_page',default=10,toType='int')
        
        view_bar_name=self.getConfig('btn_nav',default='视图操作区',toType='str')
        self.view_bar_name = view_bar_name
        self.view_bar = None
        view_actionbar_name=self.getConfig('btn_action',default='业务操作区',toType='str')
        self.view_actionbar_name = view_actionbar_name
        self.view_actionbar = None


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
            '点击文档':self.click_doc,
            '双击文档':self.dblclick_doc,
            '选择文档':self.open_doc,
            '文档存在':self.chk_is_exist,
            '文档不存在':self.chk_not_exist,
            '视图导航':self.view_nav,
            '视图操作':self.view_action
        }
        
        if switch.has_key(action):
            return switch[action](para,context)
        else:
            print('action %s is invalid!!!' % action) 
            raise Exception('action %s is invalid!!!' % action)
    #检查视图是否加载完成
    def ready(self,delay=5,count=20):
        selector_chk = self.getConfig('selector_check',default='',toType='str')
        if selector_chk=="":
            raise Exception('not found the css selector setting for view checking in context')
            return
        
        #driver = self.handle.driver
        ready = False
        count = 30
        delay = 2
        
        while not ready and count>0:
            count=count-1
            try:
                tbl = self.el.find_element_by_css_selector(selector_chk)
            except:
                sleep(delay)
                continue
            #todo容器没问题了，但还要检查视图内容是否出现
            try:
                trs = tbl.find_elements_by_tag_name('tr')
            except:
                sleep(delay)
                continue
            if (len(trs)>0):
                #有内容了，退出等待循环，设置成功标志
                ready=True
        return ready
    def nav(self,pagenum):
        if (pagenum>0):
            for i in range(0,pagenum):
                found=self.view_nav('下一页')
                if(found=='disabled'):
                    break
        elif (pagenum<0):
            for i in range(0,-pagenum):
                found=self.view_nav('上一页')
                if(found=='disabled'):
                    break
                    
    #触发视图操作（为方便，输入操作的部分文本即可，有多个匹配，触发第一个）,可用于翻页等视图操作
    def view_nav(self, label,context={}):
        
        view_bar_name=self.view_bar_name
        if view_bar_name.lower()=='none':
            return False
        if(view_bar_name!='' and self.view_bar==None):
            self.view_bar = Plug_btn_bar(self.handle,view_bar_name)
        
        found = self.view_bar.send(label,context)
        return found
    #触发业务操作（为方便，输入操作的部分文本即可，有多个匹配，触发第一个）,可用于视图上的业务操作
    def view_action(self, label,context={}):
        view_actionbar_name=self.view_actionbar_name
        if(view_actionbar_name!='' and self.view_actionbar==None):
            self.view_actionbar = Plug_btn_bar(self.handle,view_actionbar_name)
        
        found = self.view_actionbar.send(label,context)
        return found
    #从页面获取所有视图页签名称，返回数组
    
    def chk_is_exist(self,docTitle,context={}):
        print(('扩展：在视图（%s）中检查文档(%s)存在' % (self.el_name,docTitle)).decode(__default_encoding__))
        
        if not self.isDocInView(docTitle,context=context,max_try=self.max_page):
            #文档未找到，抛异常退出
            raise Exception(('扩展：在视图（%s）中文档(%s)不存在' % (self.el_name,docTitle)))
        
    def chk_not_exist(self,docTitle,context={}):
        print(('扩展：在视图（%s）中验证文档(%s)不存在' % (self.el_name,docTitle)).decode(__default_encoding__))
        
        if self.isDocInView(docTitle,context=context,max_try=self.max_page):
            #文档竟然找到，抛异常退出
            raise Exception(('扩展：在视图（%s）中文档(%s)还存在' % (self.el_name,docTitle)))

    def isDocInView(self,docTitle,context={},max_try=10):
        #尝试回到视图第一页，从头找起
        self.view_nav('首页')
        
        for i in range(0,max_try-1):
            row = self.view_body.getRow(docTitle)

            if row!=None:
                return True
            else:
                #尝试翻页以后再检查
                next_found = self.view_nav('下一页')
                if (not next_found=='True'):
                    break
        #没有找到，返回False
        return False
    
    def dblclick_doc(self,docTitle,context={},max_try=10):
        self.click_doc(docTitle,context=context,max_try=max_try,click_mode='doubleclick')
    def click_doc(self,docTitle,context={},max_try=10,click_mode='click'):
        print(('扩展：在视图（%s）中%s文档(%s)' % (self.el_name,click_mode,docTitle)).decode(__default_encoding__))
        
        for i in range(0,max_try-1):
            print(i)
            success = self.view_body.clickRow(docTitle,click_mode=click_mode)
            '''
            try:
                print(i)
                success = self.view_body.clickRow(docTitle)
            except:
                #found but failure in clicking the element
                raise Exception('some error occurrs while clicking document(%s) in View(%s)' % (docTitle,self.el_name))
            '''
            if (success):
                sleep(2)
                return True
            else:
                #尝试翻页以后再检查
                next_found = self.view_nav('下一页')
                sleep(3)
                if (not next_found or i==max_try-1):
                    #下一页按钮没找到，或禁用了，则终止翻页处理
                    print('The doc(%s) is not found in view(%s) after (%i) tries' % (docTitle.decode(__default_encoding__),self.el_name.decode(__default_encoding__),i+1))
                    break
        raise  Exception('can not select the doc(%s) in view(%s)' % (docTitle,self.el_name))
        #sleep(1)
        return False
    def select_doc(self,docTitle,context={},max_try=10):
        print(('扩展：在视图（%s）中选中文档(%s)' % (self.el_name,docTitle)).decode(__default_encoding__))
        
        for i in range(0,max_try-1):
            print('page:%i' % (i+1))
            row = self.view_body.getRow(docTitle)
            '''
            try:
                print(i)
                success = self.view_body.clickRow(docTitle)
            except:
                #found but failure in clicking the element
                raise Exception('some error occurrs while clicking document(%s) in View(%s)' % (docTitle,self.el_name))
            '''
            if (row != None):
                success = self.view_body.selectRow(row,context=context)
                if success:
                    sleep(2)
                    return True
                else:
                    raise Exception('can not select the doc(%s) in view(%s)' % (docTitle,self.el_name))
            else:
                #尝试翻页以后再检查
                next_found = self.view_nav('下一页')
                sleep(3)
                if (not next_found=='True' or i==max_try-1):
                    #下一页按钮没找到，或禁用了，则终止翻页处理
                    print('The doc(%s) is not found in view(%s) after (%i) tries' % (docTitle.decode(__default_encoding__),self.el_name.decode(__default_encoding__),i+1))
                    break
        sleep(1)
        return False
    def open_doc(self,docTitle,context={}):
        
        print(('扩展：在视图（%s）中处理文档(%s)' % (self.el_name,docTitle)).decode(__default_encoding__))
        #处理用于打开文档的操作按钮,例如编辑标题为abc的文档，则 编辑信息|abc
        pos = docTitle.find('|')
        if pos>0:
            button_label = docTitle[0:pos]
            docTitle = docTitle[pos+1:]
        else:
            button_label = ''
        
        if self.select_doc(docTitle,context=context,max_try=self.max_page) and button_label!='':
            self.view_action(button_label)
            sleep(self.wait)
        else:
            raise Exception('can not select the doc(%s) in view(%s)' % (docTitle,self.el_name))
    '''    
    def del_doc(self,docTitle,context={}):
        print(('扩展：在视图（%s）中删除文档(%s)' % (self.el_name,docTitle)).decode(__default_encoding__))
        #处理用于打开文档的操作按钮
        button_label = self.getConfig('btn_label',default='删除',toType='str')
        #处理用于打开文档的操作按钮,例如删除标题为abc的文档，则 删除|abc
        pos = docTitle.find('|')
        if pos>0:
            button_label = docTitle[0:pos]
            docTitle = docTitle[pos+1:]
        elif pos==0:
            button_label = '删除'
            docTitle = docTitle[1:]
        else:
            button_label = '删除'
        
        if self.select_doc(docTitle,context=context,max_try=self.max_page):
            self.view_action(button_label)
            sleep(self.wait)
    '''    

    
