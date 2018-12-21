#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 15:30
# test_case/test_case_1/start_case_01.py
import pdb


import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import unittest
import os
import time


from config import currentProject
oa_init=currentProject.innerload('ext.function.oa_init')
oa_try=currentProject.innerload('ext.function.oa_try')

# 用例
class Case_01(unittest.TestCase):
    ''' 组织用户管理回归测试
        hello
    '''
    def setUp(self):
        pass

    def test_zzk(self):
        ''' 空测试,空方法
            next
        '''
        #search("哇塞好玩")
        print('空方法：test_zzk')
        print(currentProject.id)

    def test_poc_01(self):
        '''用户管理基本功能（新建、查询、删除）
        '''
        uihandle = oa_init()
        
        docTitle = "回归测试%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]党办文件（自动测试）20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='poc用户管理',retry=0)
    def test_poc_02(self):
        '''组织管理基本功能（新建、查询、删除）
        '''
        uihandle = oa_init()
        
        docTitle = "回归测试%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]党办文件（自动测试）20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='poc组织管理',retry=0)
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()