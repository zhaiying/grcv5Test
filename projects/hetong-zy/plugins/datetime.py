#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-01-15 13:20
# plugins/addressbook.py

from log.log import Logger
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC

import re


from encapsulation.fields import BaseField
#pdb.set_trace()
from config import currentProject

#from frame import Model_Frame
#from base import Plug_btn_bar


#插件中不能使用innerload访问ext.models，因为models中引用了plugins.*，会产生循环调用，此处已经修改
# 界面测试组件维护在此--基本界面组件
# 包括 日期选择器 datetimepicker



class Plug_DT_Picker(BaseField):
    '''视图功能
    '''
    f_type='datetime_picker'
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        months=['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月']
        months_table={}
        i=0
        for month in months:
            months_table[month.decode(__default_encoding__)]=i
            i=i+1
        self.months=months
        self.months_table=months_table
        
        self.handle=uihandle
        #编辑器帧
        
        el = self.handle.element(page,element,siteName=siteName,context=context)
        self.el=el 
        self.el_name=element
        self.context=context
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
        
    def send(self, value='',context={}):
        self.open()
        
        #解析处理对编辑器的操作
        seperators = '-/'
        values = re.split('['+seperators+']',value)
        if len(values)<3:
            print( 'wrong date time format %s' % value)
        year = int(values[0])
        month = int(values[1])
        day = int(values[2])
        
        self.setDate(year,month,day)
        
            
        sleep(self.wait)
    def setDate(self,year,month,day):
        day_switch=self.handle.driver.find_element_by_css_selector('div.datetimepicker-days table.table-condensed th.switch')
        
        switch_label = day_switch.text
        labels = switch_label.split(' ')
        cur_year = int(labels[1])
        cur_month = self.months_table[labels[0]]
        
        if year!=cur_year:
            day_switch=self.handle.driver.find_element_by_css_selector('div.datetimepicker-days table.table-condensed th.switch')
            day_switch.click()
            
            month_switch=self.handle.driver.find_element_by_css_selector('div.datetimepicker-months table.table-condensed th.switch')
            month_switch.click()
            
            self.setYear(year,month,day)
        elif month!=cur_month:
            day_switch=self.handle.driver.find_element_by_css_selector('div.datetimepicker-days table.table-condensed th.switch')
            day_switch.click()
            
            month_switch.click()
            self.setMonth(month,day)
        else:
            self.setDay(day)
        
    def setYear(self,year,month,day):
        
        year_switch=self.handle.driver.find_element_by_css_selector('div.datetimepicker-years table.table-condensed th.switch')
        
        switch_label = year_switch.text
        a_year = switch_label.split('-')
        lower_year = int(a_year[0])
        upper_year = int(a_year[1])
        
        if year<lower_year:
            year_prev=self.handle.driver.find_element_by_css_selector('div.datetimepicker-years table.table-condensed th.prev')
            year_prev.click()
            self.setYear(year,month,day)
        elif year>upper_year:
            year_next=self.handle.driver.find_element_by_css_selector('div.datetimepicker-years table.table-condensed th.next')
            year_next.click()
            self.setYear(year,month,day)
        else:
            years = self.handle.driver.find_elements_by_css_selector('div.datetimepicker-years table.table-condensed span.year')
            for y in years:
                if str(year) in y.text:
                    y.click()
                    break
            self.setMonth(month,day)
        
    def setMonth(self,month,day):
        
        months = self.handle.driver.find_elements_by_css_selector('div.datetimepicker-months table.table-condensed span.month')
        for m in months:
            if month == self.months_table[m.text] + 1:
                m.click()
                break
        self.setDay(day)
    def setDay(self,day):
        
        days=self.handle.driver.find_elements_by_css_selector('div.datetimepicker-days table.table-condensed td.day')

        for d in days:
            if day == int(d.text) and not 'old' in d.get_attribute('class'):
                d.click()
                break
    def open(self):
        btn=self.el.find_element_by_css_selector('span.glyphicon.glyphicon-calendar')
        btn.click()
        
        

    
