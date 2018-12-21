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
# 包括 transition

class Plug_transition(BaseField):
    '''扩展操作功能，用于处理不同分支引起的后续操作的不同，例如正常提交，需要选择后续处理人，而驳回到发起人，则只需要确认操作
    '''
    f_type='transition'
    def __init__(self,uihandle,element='',page="", siteName="",context={}):
        self.handle=uihandle
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be uzsed at last.
        self.wait_for_begin=self.getConfig('wait_for_begin',default=0,toType='float')
        self.wait=self.getConfig('wait',default=0,toType='float')
        
    def send(self, actions='',context={}):
        sleep(self.wait_for_begin)
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
            '退回-重走流程|驳回':self.back_retry,
            '退回-直接提交':self.back_back,
            '加签':self.cjs_join,
            '减签':self.cjs_split,
            '反馈送阅|反馈沟通':self.feedback,
            '沟通|转办':self.communicate,
            '撤销沟通':self.dis_communicate,
            '返回':self.abort,
            'default':self.process
        }
        default=None
        for sw in switch:
            sw_a = sw.split('|')
            if action in sw_a:
                return switch[sw](action,para,context)
            elif not default and 'default' in sw_a:
                #允许设置自定义值
                default = switch[sw]
        
        #执行到此，说明没有找到精确匹配，那么执行default操作，如果default操作也没有设置，那么执行process
        if default:
            return default(action,para,context)
        else:
            return process(action,para,context)
            
    def process(self,action, v,context={}):
        uihandle = self.handle
        values=self.parse(v)
        
        uihandle.fillForm('下一步_正向操作',context=context,skip_empty_field=True,skip_empty_form=True)
    def abort(self,action, v,context={}):
        uihandle = self.handle
        values=self.parse(v)
        
        uihandle.field('业务表单操作区',context['transition'].strip(),'btn_bar')
        uihandle.field('提示窗口','ok','alert')
    def back_retry(self,action, v,context={}):
        self.back_operation('重走流程', v, context=context)
    def back_back(self,action, v,context={}):
        self.back_operation('直接提交到本环节', v, context=context)
    def back_operation(self,action, v,context={}):
        
        #处理返回选项
        uihandle = self.handle
        uihandle.field('业务表单操作区','退回','btn_bar')
        line = uihandle.find_element(['css selector','ul.dropdown-menu>li'],text=action)
        option = line.find_element_by_css_selector('input[type=radio]')
        option.click()
		
        button = uihandle.find_element(['css selector','ul.dropdown-menu>li>a'],text=v)
        button.click()
        '''
        values=self.parse(v)
        self.handle.field('下一步操作区','编号','btn_bar',context=context)
        for itm in values:
            if itm == '类别':
                self.handle.field('操作_编号_编号类型',values[itm],'select',context=context)
            elif itm == '值':
                self.handle.field('操作_编号_编号值',values[itm],'input',context=context)
        self.handle.field('弹出框_确定','','button',context=context)
        '''
    def cjs_join(self,action, v,context={}):
        
        #处理加签操作
        if context.has_key('assignee'):
            assignee = context['assignee']
        else:
            assignee = ''
        uihandle = self.handle
        uihandle.field('业务表单操作区',action,'btn_bar')
        uihandle.field('加签_参与者选择',assignee,'org_ztree')
    def cjs_split(self,action, v,context={}):
        if context.has_key('assignee'):
            assignee = context['assignee']
        else:
            assignee = ''
            
        #进行视图文档参数格式处理
        seperators=',;'  #支持的分隔符
        list = re.split('['+seperators+']',assignee)
        for i in range(0,len(list)):
            list[i] = '点击文档=%s' % list[i]
        value = ','.join(list)
        
        #处理减签操作
        uihandle = self.handle
        sleep(0.5)
        uihandle.field('业务表单操作区',action,'btn_bar')
        sleep(1)
        uihandle.field('减签_选择视图',value,'view_panel')
        uihandle.field('弹出框_按钮区','确认','btn_bar')
        sleep(0.5)
        uihandle.field('业务表单操作区','返回','btn_bar')
        
        sleep(0.5)
    def feedback(self,action, v,context={}):
        
        #处理反馈传阅操作
        uihandle = self.handle
        sleep(0.5)
        uihandle.field('业务表单操作区',action,'btn_bar')
        #sleep(1.5)
        
        #uihandle.field('业务表单操作区','返回','btn_bar')
        
        sleep(0.5)
        
    def communicate(self,action, v,context={}):
        
        #处理沟通操作，沟通参与人
        if context.has_key('assignee'):
            assignee = context['assignee']
        else:
            assignee = ''
        
        uihandle = self.handle
        uihandle.field('业务表单操作区',action,'btn_bar')
        uihandle.field('沟通_选择人员',assignee,'org_ztree')
        
    def dis_communicate(self,action, v,context={}):
        if context.has_key('assignee'):
            assignee = context['assignee']
        else:
            assignee = ''
            
        #处理撤销沟通操作
        uihandle = self.handle
        sleep(0.5)
        uihandle.field('业务表单操作区',action,'btn_bar')
        sleep(0.5)
        items = uihandle.driver.find_elements_by_css_selector('div.modal-dialog div.modal-body>table td')
        self.list_click(items,assignee)
        
        sleep(1)
        uihandle.field('弹出框_按钮区','确认','btn_bar')
        sleep(0.5)
        
    def list_click(self, obj_list,assignee):
        seperators=',;'  #支持的分隔符
        name_list = re.split('['+seperators+']',assignee)
        
        
        for obj in obj_list:
            label = '全选'.decode(__default_encoding__).strip()
            if label == obj.text.strip():
                chk = obj.find_element_by_css_selector('input')
                if chk.is_selected():
                    
                    chk.click()
                break
        
        for name in name_list:
            found=False
            label = name.decode(__default_encoding__).strip()
            for obj in obj_list:
                if label == obj.text.strip():
                    chk = obj.find_element_by_css_selector('input')
                    if not chk.is_selected():
                        
                        chk.click()
                    found=True
                    break
            if not found:
                #如果有assignee没有找到，应该抛异常
                raise Exception('user(%s) not found' % name)
        
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
 
    
