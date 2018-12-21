#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-08-15 13:20

import time
def dur( op=None, clock=[time.time()] ):
    if op != None:
        duration = time.time() - clock[0]
        print('========%s finished. Duration %.6f seconds.' % (op, duration))
    clock[0] = time.time()

def regMainDep(depname,depcode):
    
    uihandle.field('组织用户管理_新建机构','',type='button')
    sleep(1)
    uihandle.field('新建机构_机构代码','orgtest_%s' % depcode,type='input')
    uihandle.field('新建机构_名称',depname,type='input')
    uihandle.field('新建机构_机构级别','公司',type='select')
    uihandle.field('新建机构_排序序号',str(int(depcode)+100),type='input')
    
    uihandle.field('新建机构_备注信息','为性能测试自动测试添加，系统上线后应予删除',type='input')
    
    uihandle.field('新建用户_确定','',type='button')
    sleep(3)
def regDep(depname,depcode):
    
    uihandle.field('组织用户管理_新建机构','',type='button')
    sleep(1)
    uihandle.field('新建机构_机构代码','orgtest_%s' % depcode,type='input')
    uihandle.field('新建机构_名称',depname,type='input')
    uihandle.field('新建机构_机构级别','分子公司',type='select')
    uihandle.field('新建机构_排序序号',str(int(depcode)+100),type='input')
    
    uihandle.field('新建机构_备注信息','为性能测试自动测试添加，系统上线后应予删除',type='input')
    
    uihandle.field('新建用户_确定','',type='button')
    sleep(5)

from config.config_01 import browser_config
from encapsulation.webdriver.myerrorhandler import MyErrorHandler

from time import sleep
import time
import re
from log.log import Logger

from selenium.webdriver.common.action_chains import ActionChains as AC
from config import currentProject

SmartHandle=currentProject.innerload('ext.models.SmartHandle')
View=currentProject.innerload('ext.models.View')
Workflow=currentProject.innerload('ext.models.Workflow')
WorkflowNode=currentProject.innerload('ext.models.WorkflowNode')
Form=currentProject.innerload('ext.models.Form')

oa_init=currentProject.innerload('ext.function.oa_init')
oa_login=currentProject.innerload('ext.function.oa_login')
oa_try=currentProject.innerload('ext.function.oa_try')

flow = '用户管理基本功能'
docTitle='testdoc'

dur()
uihandle = oa_init()
driver = uihandle.driver
dur('init')

user = '系统管理员'
deps=['']
for i in range(2,11):
    deps.append(str(i).rjust(2,'0'))

oa_login(uihandle,user,simple=True)
dur('login')

from encapsulation.plugins import *
from encapsulation.fields import BaseField
sleep(3)
#uihandle.field('主页栏目','个人办公',type='btn_bar')
#sleep(3)
uihandle.field('oa主导航按钮区','应用管理',type='btn_bar')
sleep(3)
#uihandle.field('系统主导航菜单','系统管理/组织用户管理',type='sys_menu')
uihandle.field('系统主导航菜单','组织和权限/组织用户管理',type='sys_menu')
sleep(0.5)
uihandle.field('组织用户管理_组织机构选择','组织机构',type='org_ztree')
sleep(0.5)
dur('switch')

regMainDep('测试部门','000')
sleep(1)
uihandle.field('组织用户管理_组织机构选择','组织机构/测试部门',type='org_ztree')
sleep(0.5)

i_start=1
i_end=11

for i in range(i_start,i_end):
    
    dep = '测试机构%s' % deps[i-1]
    regDep(dep,str(i).rjust(3,'0'))
dur('register departments')
    