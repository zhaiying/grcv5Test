#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 15:30
# test_case/test_case_flow/start_case_01.py

import unittest
from config import currentProject

oa_init=currentProject.innerload('ext.function.oa_init')
oa_try=currentProject.innerload('ext.function.oa_try')

SmartHandle=currentProject.innerload('ext.models.SmartHandle')

from encapsulation.system import SysContext
sys_context = SysContext()


# 用例
class Case_user(unittest.TestCase):
    '''组织用户管理回归测试
    '''
    def setUp(self):
        pass
    def test_poc_00(self):
        '''新建和删除用户
        '''
        runpaths = sys_context.get_raw('runpaths',scope='global')
        resume = int(sys_context.get_raw('resume',default='0',scope='global'))
        retry = int(sys_context.get_raw('retry',default='0',scope='global'))
        flow = sys_context.get_raw('flow',default='poc基本功能',scope='global')

        print('%s:%s:--%i--%i' % (flow,runpaths,resume,retry))
        #uihandle = oa_init()
        uihandle = SmartHandle()
        uihandle.sysContext = sys_context
        oa_try(self,uihandle,docTitle='',runPaths=runpaths,resume=resume,flow=flow,retry=retry)
        
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
    