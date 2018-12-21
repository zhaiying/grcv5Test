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

#����в���ʹ��innerload����ext.models����Ϊmodels��������plugins.*�������ѭ�����ã��˴��Ѿ��޸�
# ����������ά���ڴ�--ϵͳ�ڲ����
# ���� dialog

class Plug_dialog(BaseField):
    '''��չ�������ܣ����ڴ���ͬ������ʹ�õĲ�ͬ�ġ����͡��Ի��򣬴���Ի������ͺͲ�������
    '''
    f_type='dialog'
    def __init__(self,uihandle,element='',page="", siteName="",context={}):
        self.handle=uihandle
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be used at last.
        self.wait_for_begin=self.getConfig('wait_for_begin',default=0,toType='float')
        self.wait=self.getConfig('wait',default=0,toType='float')
        
    def send(self, actions='',context={}):
        sleep(self.wait_for_begin)
        #���������ϵͳ�����Ĳ���
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
            '����ѡ��':self.flow_chooser,
            'default':self.default_dialog
        }
        default=None
        for sw in switch:
            sw_a = sw.split('|')
            if action in sw_a:
                return switch[sw](action,para,context)
            elif not default and 'default' in sw_a:
                #���������Զ���ֵ
                default = switch[sw]
        
        #ִ�е��ˣ�˵��û���ҵ���ȷƥ�䣬��ôִ��default���������default����Ҳû�����ã���ôִ��process
        if default:
            return default(action,para,context)
        else:
            return default_dialog(action,para,context)
            
    def default_dialog(self,action, v,context={}):
        uihandle = self.handle
        #�ݲ�����ȱʡ�Ի����Ժ���Ҫ��ʱ����ʵ��
        return
        
    def flow_chooser(self,action, v,context={}):
        
        #�����緢�ļ�ְ���ѡ��
        uihandle = self.handle
        driver = uihandle.driver
        '''
        #���л�������ѡ���֡��
        frame = driver.find_element_by_css_selector('iframe#showDeptName')
        driver.switch_to_frame(frame)
        '''
        #����ѡ��
        els = driver.find_elements_by_css_selector('table#selectContractFlowTable tr')
        
        key,value = self.parseCondition(v)
        
        found = False
        el_choosed = None
        if key=='seq':
            #�����ѡ��
            if value>0 and value<=len(els):
                el_choosed = els[value-1]
            elif value<0 and -value<=len(els):
                #����ѡ��
                el_choosed = els[value]
            else:
                raise Exception('Wrong parameter(seq=%i)! There is only %i row in chooser table!' % (value,len(els)))
        else:
            
            dest_str = value.decode(__default_encoding__)
            for el in els:
                if key in ['text','��������','����','name']:
                    
                    key_cols = el.find_elements_by_css_selector('td[colindex="2"]')
                    if len(key_cols)==0:
                        continue
                    cur_str = key_cols[0].text
                    if dest_str in cur_str:
                        el_choosed = el
                        found=True
                        break
                if key in ['id','���̱���','����','code']:
                    
                    key_cols = el.find_elements_by_css_selector('td[colindex="1"]')
                    if len(key_cols)==0:
                        continue
                    cur_str = key_cols[0].text
                    if dest_str in cur_str:
                        el_choosed = el
                        found=True
                        break
        if found:
            self.clickRow(el_choosed)
            uihandle.field('������_ȷ��','','button')
        else:
            raise Exception('chooser(%s) not found' % v)

        sleep(self.wait)
        
    def clickRow(self,el):
        if el:
            
            
            click_node = el.find_element_by_css_selector('input[type=checkbox]')
            if not click_node.is_selected():
                click_node.click()
            
    def parse(self,val):
        #������Ĳ�����ֵ��,��|Ϊ�ָ��������ֻ��һ����������ô����ѡ��������������������ô��һ�������ǰ�ť������ȷ����ȡ����ʹ��ȡ������Ϊ����֤���ѡ���Ƿ���ڡ��ڻ�����ת���У�һ��ѡ����ҵ�����ͣ���ȷ�����ͻ�����������Ӧ�ķ��������Ϊ��ֻ�����ԣ������ȡ���İ�ťѡ�񣩣��ڶ���������ѡ����
        pos = val.find('|')
        if pos>0:
            paraName = val[0:pos]
            paraValue = val[pos+1:]
        else:
            paraName = ''
            paraValue = val
        
        return (paraName,paraValue)
        
    def parseCondition(self,condition):
        
        pos = condition.find('|')
        if pos>0:
            it=condition[:pos]
            v=condition[pos+1:]
        else:
            it='text'
            v=condition
        if it=='seq':
            v=int(v)
        return it,v
    def Condition(self,el,condition,seq=0):
        item = condition.strip()
        pos = item.find('|')
        if pos>0:
            it=item[:pos]
            v=item[pos+1:]
        else:
            it='text'
            v=item
        if it=='id':
            return (v.decode(__default_encoding__) in el.get_attribute('id'))
        elif it=='seq':
            return seq==int(v)
        else:
            return (v.decode(__default_encoding__) in el.get_attribute('innerText'))
