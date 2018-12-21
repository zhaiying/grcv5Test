#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 15:30
# test_case/test_case_flow/start_case_01.py

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

from config import currentProject
oa_init=currentProject.innerload('ext.function.oa_init')
oa_try=currentProject.innerload('ext.function.oa_try')

import time

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
# 用例
class Case_user(unittest.TestCase):
    '''业务流程回归测试
    '''
    def setUp(self):
        pass
    def ttttest_flow_01(self):
        '''政企分公司-党办文件 20171226
        '''
        uihandle = oa_init()
        
        docTitle = "党办文件（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]党办文件（自动测试）20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司党办文件',retry=5)
    def test_poc_00(self):
        '''发文基本流程
        '''
        
        uihandle = oa_init()
        
        docTitle = "新建用户回归测试%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]党办文件（自动测试）20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='poc基本功能',retry=3)
    def test_zzk2(self):
        ''' 空测试2
            next
        '''
        #search("哇塞好玩")
        print('空方法2：test_zzk2')
        print(currentProject.id)
        
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()