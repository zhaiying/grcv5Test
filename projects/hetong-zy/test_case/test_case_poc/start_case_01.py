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

# ����
class Case_01(unittest.TestCase):
    ''' ��֯�û�����ع����
        hello
    '''
    def setUp(self):
        pass

    def test_zzk(self):
        ''' �ղ���,�շ���
            next
        '''
        #search("��������")
        print('�շ�����test_zzk')
        print(currentProject.id)

    def test_poc_01(self):
        '''�û�����������ܣ��½�����ѯ��ɾ����
        '''
        uihandle = oa_init()
        
        docTitle = "�ع����%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[����ֹ�˾]�����ļ����Զ����ԣ�20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='poc�û�����',retry=0)
    def test_poc_02(self):
        '''��֯����������ܣ��½�����ѯ��ɾ����
        '''
        uihandle = oa_init()
        
        docTitle = "�ع����%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[����ֹ�˾]�����ļ����Զ����ԣ�20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='poc��֯����',retry=0)
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()