#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 13:20
# encapsulation/fields.py
from time import sleep

class BaseField(object):
    ''' base model of field-like object. provide base inteface for invoke
    '''
    f_type='base_field'
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        self.handle=uihandle
        el = uihandle.element(page, element, siteName,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def send(self,msg,context={}):
        #填写字段内容
        pass
        
    def clear(self):
        #填写字段内容
        pass
    
    def getConfig(self,key,default='',toType='str'):
        return self.handle.siteConfig.getExtraInfo(self.context,key,default,toType)
    def getElement(self,element):
        #同时支持锚点和选择器的方式选择元素
        ref = element.strip()
        if ref.lower().startswith('id='):
            selector = ['id',ref[3:]]
        elif ref.lower().startswith('css selector='):
            selector = ['css selector',ref[13:]]
        else:
            selector = ''
        if selector=='':
            #元素锚名称查询
            el = self.handle.element('',ref,context=self.context)
        else:
            el = self.handle.find_element(selector,context=self.context)
        return el
        
    @classmethod
    def type(cls):
        return cls.f_type
    