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
# ����
class Case_user(unittest.TestCase):
    '''ҵ�����̻ع����
    '''
    def setUp(self):
        pass
    def ttttest_flow_01(self):
        '''����ֹ�˾-�����ļ� 20171226
        '''
        uihandle = oa_init()
        
        docTitle = "�����ļ����Զ����ԣ�%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[����ֹ�˾]�����ļ����Զ����ԣ�20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='����ֹ�˾�����ļ�',retry=5)
    def test_poc_00(self):
        '''���Ļ�������
        '''
        
        uihandle = oa_init()
        
        docTitle = "�½��û��ع����%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[����ֹ�˾]�����ļ����Զ����ԣ�20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='poc��������',retry=3)
    def test_zzk2(self):
        ''' �ղ���2
            next
        '''
        #search("��������")
        print('�շ���2��test_zzk2')
        print(currentProject.id)
        
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()