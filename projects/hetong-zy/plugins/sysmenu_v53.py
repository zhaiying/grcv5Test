#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-01-15 13:20
# plugins/sysmenu.py

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
#from model import Model_SysMenu

# 界面测试组件维护在此--基本界面组件
# 包括 sys_menu

class Plug_Sys_Menu(BaseField):
    '''系统菜单
    '''
    f_type='sys_menu'
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        #与ztree原型不同，界面模型使用触发按钮作为element，需要转换一下
        el=Model_SysMenu_v7(uihandle,element,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
            
    def send(self,selections,context={}):
        
        self.el.send(selections)
        sleep(self.wait)

#系统菜单对象
class Model_SysMenu_v7(BaseField):
    '''系统菜单类型
    特点是 每一级菜单是li,第二级以下是dt,dd,a
    '''
    f_type='SysMenu_base_v7'
    def __init__(self, uihandle, element='系统主导航菜单',context={}):
        self.handle = uihandle
        self.el_name = element
        self.context=context
    def send(self,menus):
        if(menus==""):
            return
        seperator='/'
        
        root = self.handle.element('',self.el_name)
        self.click(root,menus)
        
    def click(self,cntr_node,menus,level=0):
        #递归查询菜单
        found = False
        if(menus==""):
            #the sub-menus is empty, so all the menus have been found 
            return True
        seperator='/'
        menus_a = menus.split(seperator)
        label=menus_a[0]
        
        first_node = self.first_level_node(cntr_node,label)
        if first_node!=None and len(menus_a)>1:
            label=menus_a[1]
            second_node = self.second_level_node(first_node,label)
            found = True
        return found
    def click(self,cntr_node,menus,level=0):
        found = False
        if(menus==""):
            #the sub-menus is empty, so all the menus have been found 
            return True
        seperator='/'
        menus_a = menus.split(seperator)
        label=menus_a[0]
        
        nodes = cntr_node.find_elements_by_css_selector('li')
        for i in range(0,len(nodes)):
            titles=nodes[i].get_attribute('innerText').split('\n')
            
            if len(titles)>1 and label.decode(__default_encoding__).strip() == titles[0].strip():
                
                #单击打开当前节点
                nodes[i].click()
                sleep(0.5)
                #继续处理下一层级的菜单
                menus=seperator.join(menus_a[1:])
                found=self.click(nodes[i],menus,level=level+1)
                break
        return found
