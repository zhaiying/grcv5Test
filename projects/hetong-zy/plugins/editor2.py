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

#from frame import Model_Frame
#from base import Plug_btn_bar

#插件中不能使用innerload访问ext.models，因为models中引用了plugins.*，会产生循环调用，此处已经修改
# 界面测试组件维护在此--基本界面组件
# 包括 nkto正文编辑器 editor



class Plug_Editor2(BaseField):
    '''nkto正文功能
    '''
    f_type='editor2'
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        #编辑器帧
        
        #el = self.handle.element(page,element,siteName=siteName,context=context)
        #self.el=el 
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
        
    def send(self, actions='',context={}):
        self.handle.field('公文表单页签','正文','btn_bar')
        sleep(0.5)
        self.handle.field('红头模板选择','发文','btn_bar')
        self.handle.field('弹出框_确定','确定','btn_bar')
        sleep(1)
        '''
        #处理正文控件装载失败的提示
        alt = self.handle.driver.switch_to_alert()
        #print('alert prompt: %s' % alt.text)
        alt.accept()
        sleep(0.5)
        '''
        self.handle.field('公文表单页签','业务办理','btn_bar')
        
        '''
        #解析处理对编辑器的操作
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
        '''
    def do(self,action,para,context):
        
        switch = {
            '内容':self.set_raw_content
        }
        
        if switch.has_key(action):
            return switch[action](para,context)
        else:
            raise Exception('action %s is invalid!!!' % action)
    #设置编辑器中的内容源码
    def set_raw_content(self, raw_content,context={}):
        btn_source=self.el.find_element_by_css_selector('a.rs_ed_btn[val=source]')
        btn_source.click()
        #raw_field=self.el.find_element_by_css_selector('textarea#content_view')
        #raw_field.text=raw_content
        self.executeInput('textarea#content_view',raw_content.decode(__default_encoding__))
        btn_visual=self.el.find_element_by_css_selector('a.rs_ed_btn[val=visual]')
        btn_visual.click()
    def click_button(self,value=''):
        els = self.el.find_element_by_css_selector('a.rs_ed_btn')
        i=0
        label=value.decode(__default_encoding__)
        found = 'False'
        for l in els:
            if(label in l.get_attribute('innerText')):
                c = l.get_attribute('class')
                if (not 'disabled' in c ):
                    l.click()
                    sleep(1)
                    found = 'True'
                    break
                else:
                    print('the action(%s) had already been disbled, so ignore it' % label.decode(__default_encoding__))
                    found = 'disabled'
                    break
            i=i+1
        if found=='False':
            print('the action(%s) does no exist, so ignore it' % label.decode(__default_encoding__))
        
        sleep(self.wait)
        return found
    def executeInput(self,css_selector,value):
        #pdb.set_trace()
        el = self.el.find_element_by_css_selector(css_selector)
        id = el.get_attribute('id')
        if (id==''):
            name = el.get_attribute('name')
            selector = '*[name="%s"]' % name
        else:
            selector = '#%s' % id
        script = "(function(sel,value){$(sel).val(value);}('"+selector+"','"+value+"'))"
        print('script run:\n%s' % script)
        
        self.handle.driver.execute_script(script)
        
        

    
