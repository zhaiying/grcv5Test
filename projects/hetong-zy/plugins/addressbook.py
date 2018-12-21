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
from model import Model_LazyTree,Model_Ulist

# 界面测试组件维护在此--基本界面组件
# 包括 org,cjs_org,fenfa_org,person,meeting_select,common_addressbook

class Plug_org(BaseField):
    '''普通部门选择框（单多选）
    '''
    f_type='org'
    f_open=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        el=Orgbook(uihandle,element,page,siteName,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def open(self):
        if(not self.f_open):
            self.el.open()
            self.f_open=True
    def close(self):
        if(self.f_open):
            self.el.close()
            self.f_open=False
    def send(self,selections,context={}):
        self.open()
        self.el.clickOrgItems(selections)
        self.close()
class Plug_cjs_org(BaseField):
    '''会签部门选择框（单多选）
    '''
    f_type='cjs_org'
    f_open=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        el=CjsOrgbook(uihandle,element,page,siteName,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def open(self):
        if(not self.f_open):
            self.el.open()
            self.f_open=True
    def close(self):
        if(self.f_open):
            self.el.close()
            self.f_open=False
    def send(self,selections,context={}):
        self.open()
        self.el.clickOrgItems(selections)
        self.close()
class Plug_fenfa_org(BaseField):
    '''中移动分发部门选择框（单多选）
    '''
    f_type='fenfa_org'
    f_open=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        el=FFOrgbook(uihandle,element,page,siteName,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def open(self):
        if(not self.f_open):
            self.el.open()
            self.f_open=True
    def close(self):
        if(self.f_open):
            self.el.close()
            self.f_open=False
    def send(self,selections,context={}):
        self.open()
        self.el.clickMultiOrgItems(selections)
        self.close()
class Plug_meeting(BaseField):
    '''中移动会议参加选择框（单多选）
    '''
    f_type='meeting_select'
    f_open=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        el=Meetingbook(uihandle,element,page,siteName,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def open(self):
        if(not self.f_open):
            self.el.open()
            self.f_open=True
    def close(self):
        if(self.f_open):
            self.el.close()
            self.f_open=False
    def send(self,selections,context={}):
        self.open()
        self.el.clickMultiOrgItems(selections)
        self.close()
class Plug_common_addressbook(BaseField):
    '''中移动通用选择框（单多选）
    '''
    f_type='common_addressbook'
    f_open=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        el=GenericSingleAddressBook(uihandle,element,page,siteName,keyName='待选',context=context,selectors={},buttons={'quit':'generic_addressbook_确定'},waits={})
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def open(self):
        if(not self.f_open):
            self.el.open()
            self.f_open=True
    def close(self):
        if(self.f_open):
            self.el.close()
            self.f_open=False
    def send(self,selections,context={}):
        self.open()
        self.el.clickMultiOrgItems(selections)
        self.close()
class Plug_person(BaseField):
    '''单选人员选择框（一层部门）(应该重构)
    '''
    f_type='person'
    f_open=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        el=Personbook(uihandle,element,page,siteName,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def open(self):
        if(not self.f_open):
            self.el.open()
            self.f_open=True
    def close(self):
        if(self.f_open):
            self.el.close()
            self.f_open=False
    def send(self,selection,context={}):
        user = self.handle.getUser(selection)
        id = user[0]
        orgLinks = user[2]
        self.open()
        self.el.expandOrgBranch(orgLinks)
        self.el.clickPersonItem(username)
        self.el.rightMove()
        self.close()
    
class Addressbook(object):
    # 构造方法，用来接收selenium调用所需的对象
    def __init__(self, handle, element, page="", siteName="",context={}):
        self.handle = handle
        self.button = handle.element(page,element,siteName,context=context)
        self.page = page
        self.siteName = siteName
        self.context = context
    #打开地址簿窗口
    def open(self):
        self.button.click()
        sleep(3)
        #self.frame = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['id','selIframe']))
        #self.handle.driver.switch_to_frame(self.frame)
    #关闭地址簿窗口
    def close(self):
        #self.handle.driver.switch_to_default_content()
        quitButton=self.handle.Click("地址簿选择确定按钮",context=self.context)
        sleep(3)
    '''
    #将选中项右移到右边窗口
    @classmethod    
    def rightMove(self):
        self.handle.Click("地址簿选择右移按钮")
    ''' 
    #点击组织item项
    def clickOrgItem(self, orgName):
        if (orgName==''):
            return
        find_str=orgName.decode(__default_encoding__)
        #xpath="//li[contains(@id,'departmentTree')]/span[contains(@id,'_switch')]/following-sibling::*[1][@title='"+find_str+"']"
        selector='#ydxyDept>li[title="'+find_str+'"]'
        item = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
        item.click()
    def clickOrgItems(self, orgLinks):
        #先把多个部门分拆
        orgs=orgLinks.split(',')
        for o in range(0,len(orgs)):
            #然后分拆部门路径
            chains=orgs[o].split('/')
            for i in range(0,len(chains)):
                self.clickOrgItem(chains[i])
                sleep(0.5)

#组织树对象    
class Orgbook(Addressbook):
    pass
#分发组织树对象    
class FFOrgbook(Addressbook):
    # 构造方法，用来接收selenium调用所需的对象
    def __init__(self, handle, element, page="", siteName="", context={}):
        self.handle = handle
        self.button = handle.element(page,element,siteName,context=context)
        self.page = page
        self.siteName = siteName
        self.context=context
    #关闭地址簿窗口
    def close(self):
        #self.handle.driver.switch_to_default_content()
        quitButton=self.handle.Click("地址簿选择确定按钮",context=self.context)
        sleep(2)
        #处理确认窗口
        try:
            #提示确认
            alt = self.handle.driver.switch_to_alert()
            print('alert prompt: %s' % alt.text)
            alt.accept()
            sleep(2)
            #确认发送成功
            alt = self.handle.driver.switch_to_alert()
            print('alert prompt: %s' % alt.text)
            alt.accept()
            
        except:
            pass
        sleep(2)
    #点击组织item项
    def clickOrgItem(self,oList, orgName):
        if (orgName==''):
            return
        oList.click(orgName)
    #在一个指定列表中添加多个部门选项，部门之间用逗号分隔
    def clickOrgItems(self, section ,orgLinks):
        #获取指定列表
        oList = Model_Ulist(self.handle,section)
        #先把多个部门分拆
        orgs=orgLinks.split(',')
        for o in range(0,len(orgs)):
            #然后分拆部门路径
            chains=orgs[o].split('/')
            for i in range(0,len(chains)):
                self.clickOrgItem(oList,chains[i])
                sleep(0.5)
    def clickMultiOrgItems(self, nameList):
        #先判断和分拆可能的多分发组织树(multi开头识别)
        multiPrefix='multi|'
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        if(nameList.startswith(multiPrefix)):
            #标识样例：multi|省公司:北京,上海;境外:辛姆巴科公司;专业:终端公司;部门列表:综合部,技术部;直属:研究院;其他单位:香港
            multiList = nameList[len(multiPrefix):].split(';') #分号分隔不同的区段
            #多区段列表显示更慢，需要多等一会
            sleep(1)
            for c in multiList:
                arr = c.split(":")
                section = arr[0]
                names = arr[1]
                self.clickOrgItems(section,names)
        else:
            #todo容错以后处理
            #self.selectSingleTree(nameList)
            pass
#会签组织树对象    
class CjsOrgbook(Addressbook):
    #点击组织item项
    def clickOrgItem(self, orgName):
        if (orgName==''):
            return
        find_str=orgName.decode(__default_encoding__)
        print("CjsOrgbook-click orgname:%s" % find_str)
        selector='#huiQianChuShi>li[title="'+find_str+'"]'
        #print(selector)
        item = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
        item.click()
class Personbook(Orgbook):
    #点击组织item项
    @classmethod    
    def clickPersonItem(self, name):
        find_str=name.decode(__default_encoding__)
        xpath="//ul[@id='waitSelect']/li[@name='"+find_str+"']"
        item = WebDriverWait(self.handle.driver, 15).until(EC.presence_of_element_located(['xpath',xpath]))
        item.click()
        sleep(3)

#基本地址簿模型
class GenericSingleAddressBook(Addressbook):
    # 构造方法，用来接收selenium调用所需的对象
    def __init__(self, handle, element, page="", siteName="",keyName='待选',context={},selectors={},buttons={},waits={}):
        self.handle = handle
        self.button = handle.element(page,element,siteName,context=context)
        self.page = page
        self.siteName = siteName
        self.keyName = keyName
        self.context = context
        #相关css选择器设置
        #--相关选择器的默认值
        sel = {}
        sel['root']='table.maintable td.col-md-1'
        sel['title']='span'
        sel['cntr']='ul[id]'
        sel['items']='li[id]'
        #用传入的参数selectors覆盖默认值
        sel_inst = dict(sel,**selectors)
        self.selectors = sel_inst
        #--相关按钮的默认值
        btns = {}
        btns['quit']='会议纪要_选人确定'
        self.buttons = dict(btns,**buttons)
        #--等待时间的默认值
        ws = {}
        ws['quit_before'] = 0
        ws['quit_after']= 2
        self.waits = dict(ws,**waits)
    #关闭地址簿窗口
    def close(self):
        #self.handle.driver.switch_to_default_content()
        self.wait(self.waits['quit_before'])
        
        element = self.buttons['quit']
        quitButton=self.handle.Click(element,context=self.context)
        
        self.wait(self.waits['quit_after'])
    #等待延时
    def wait(self,_time):
        try:
            t = float(_time)
            sleep(t)
        except:
            print('Waiting time setting(%s) error, ignored it' % _time)
    #点击组织item项
    def clickOrgItem(self, name,section='待选'):
        if (name==''):
            return
        oTree = Model_LazyTree(self.handle,section, self.selectors)
        oTree.ready()
        oTree.expand(name)
        
    #在一个指定列表中添加多个部门选项，部门之间用逗号分隔
    def clickOrgItems(self, section ,orgLinks):
        #获取指定列表
        oTree = Model_LazyTree(self.handle,section, self.selectors)
        #等待LazyTree加载完成
        oTree.ready()
        oTree.expandAll(orgLinks)
    def clickMultiOrgItems(self, nameList):
        #先判断和分拆可能的多分发组织树(multi开头识别)
        multiPrefix='multi|'
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        if(nameList.startswith(multiPrefix)):
            #标识样例：multi|省公司:北京,上海;境外:辛姆巴科公司;专业:终端公司;部门列表:综合部,技术部;直属:研究院;其他单位:香港
            multiList = nameList[len(multiPrefix):].split(';') #分号分隔不同的区段
            #多区段列表显示更慢，需要多等一会
            sleep(1)
            for c in multiList:
                arr = c.split(":")
                section = arr[0]
                names = arr[1]
                self.clickOrgItems(section,names)
        else:
            #单分类，默认都使用“待选”作为类别关键字
            if (':' in nameList):
                arr = c.split(":")
                section = arr[0]
                names = arr[1]
                self.clickOrgItems(section,names)
            else:
                #使用默认分类
                self.clickOrgItems(self.keyName,nameList)
            

#会议相关人组织树对象    
class Meetingbook(GenericSingleAddressBook):
    # 构造方法，用来接收selenium调用所需的对象
    def __init__(self, handle, element, page="", siteName="",keyName='待选',context={},selectors={},buttons={},waits={}):
        self.handle = handle
        self.button = handle.element(page,element,siteName,context=context)
        self.page = page
        self.siteName = siteName
        self.keyName = keyName
        self.context = context
        #相关css选择器设置
        #--默认值
        sel = {}
        sel['root']='table.maintable td.col-md-1'
        sel['title']='span'
        sel['cntr']='ul[id]'
        sel['items']='li[id]'
        
        #用传入的参数selectors覆盖默认值
        sel_inst = dict(sel,**selectors)
        self.selectors = sel_inst
        
        #--相关按钮的默认值
        btns = {}
        btns['quit']='会议纪要_选人确定'
        self.buttons = dict(btns,**buttons)
        #--等待时间的默认值
        ws = {}
        ws['quit_before'] = 0
        ws['quit_after']= 2
        self.waits = dict(ws,**waits)
            

