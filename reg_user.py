#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-08-15 13:20


import time
def dur( op=None, clock=[time.time()] ):
    if op != None:
        duration = time.time() - clock[0]
        print('========%s finished. Duration %.6f seconds.' % (op, duration))
    clock[0] = time.time()

def regUser(user):
    print('====register %s' % user)
    uihandle.field('组织用户管理_新建用户','',type='button')
    sleep(1)
    uihandle.field('新建用户_用户账号',user,type='input')
    uihandle.field('新建用户_账号密码','111111',type='input')
    uihandle.field('新建用户_重复密码','111111',type='input')
    uihandle.field('新建用户_姓名',user,type='input')
    
    #uihandle.field('新建用户_可管理机构','组织机构/信息中心',type='org_ztree',context={'find_wait':'1'})
    #uihandle.field('新建用户_分管机构','组织机构/系统管理员',type='org_ztree',context={'find_wait':'1'})
    uihandle.field('新建用户_职务','普通用户',type='select')
    
    uihandle.field('新建用户_确定','',type='button')
    #uihandle.field('新建用户_取消','',type='button')
    sleep(4)

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
dur('switch')

i_start=1
i_end=501

for i in range(i_start,i_end):
    depno=(i%100)/10
    if i==i_start or i%10==1:
        uihandle.field('组织用户管理_组织机构选择','组织机构/测试部门/测试机构%s' % deps[depno],type='org_ztree')
        sleep(0.5)
    user = 'testuser' + ('%i' % i).rjust(3,'0')
    regUser(user)
dur('register users')
    