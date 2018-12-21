#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-01-15 13:20
# plugins/base.py
from time import sleep
from encapsulation.fields import BaseField
from selenium.common.exceptions import UnexpectedAlertPresentException,NoAlertPresentException

# 界面测试组件维护在此--基本界面组件
# 包括 input,select

class Plug_input(BaseField):
    f_type='input'
    def send(self,msg,context={}):
        #填写字段内容
        self.el.clear()
        self.el.send_keys(msg)
        sleep(self.wait)
    def clear(self):
        #填写字段内容
        self.el.clear()
        sleep(self.wait)
class Plug_select(BaseField):
    f_type='select'
    def send(self,msg,context={}):
        #填写字段内容
        
        if msg.startswith('seq='):
            #seq代表列表中第几项，从1开始，负数代表从后向前数，0，代表错误的输入
            seq = 0
            c_seq = msg[4:]
            if c_seq.isdigit():
                seq = int(c_seq)
                opts=self.el.find_elements_by_tag_name('option')
                if seq>0 and seq<=len(opts):
                    opts[seq-1].click()
                    sleep(self.wait)
                    return
        else:
            #否则进行文字匹配
            opts=self.el.find_elements_by_tag_name('option')
            for opt in opts:
                if(msg in opt.text):
                    if not opt.is_selected():
                        opt.click()
                        sleep(self.wait)
                        return
        #没找到，异常退出
        raise Exception('Wrong parameter of select component:%s' % msg)         
        
class Plug_script(BaseField):
    f_type='script'
    def __init__(self,uihandle,element="",page="", siteName="",context={}):
        #因为页面代码执行不依赖锚点元素，所以element允许为空
        self.handle=uihandle
        #el = uihandle.element(page, element, siteName,context=context)
        #self.el=el
        #self.el_name=element
    def send(self,script,context={}):
        self.handle.driver.execute_script(script)
        sleep(self.wait)
class Plug_raw_input(BaseField):
    f_type='raw_input'
    def send(self,value,context={}):
        self.handle.executeInput(self.handle.driver,self.el_name,value,context=context)
        sleep(self.wait)
class Plug_button(BaseField):
    f_type='button'
    must_have_value=False
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        #因为页面代码执行不依赖锚点元素，所以element允许为空
        self.handle=uihandle
        el = uihandle.element(page, element, siteName,context=context)
        self.el=el
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def send(self,value='',context={}):
        
        self.handle.Click(self.el_name,context=context)
        
        sleep(self.wait)

class Plug_btn_bar(BaseField):
    f_type='btn_bar'
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        #因为页面代码执行不依赖锚点元素，所以element允许为空
        self.handle=uihandle
        self.page=page
        self.siteName=siteName
        #els = uihandle.elements(page, element, siteName,context=context)
        #self.els=els
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait=self.getConfig('wait',default=0,toType='float')
    def send(self,value='',context={}):
        #els = self.els
        els = self.handle.elements(self.page, self.el_name, self.siteName,context=context)
        i=0
        label=value
        found = 'False'
        for l in els:
            if(self.check(l,label)):
                c = l.get_attribute('class')
                if (not 'disabled' in c ):
                    l.click()
                    sleep(1)
                    found = 'True'
                    break
                else:
                    print('the action(%s) had already been disbled, so ignore it' % label)
                    found = 'disabled'
                    break
            i=i+1
        if found=='False':

            print('the action(%s) does no exist' % s_label)
            raise Exception('the action(%s) does no exist' % u_label)
        sleep(self.wait)
        return found
    def check(self,node,value):
        #华电项目存在多个关注按钮，只不过只有一个是不隐藏的，为了兼容这种情况，进行额外的检查，忽略那些已经隐藏或禁用的设计元素
        if not node.is_displayed() or not node.is_enabled():
            return False
        #用于检查node节点是否是需要的节点，如果是，返回True
        ret = False
        #pdb.set_trace()
        pos = value.find('=')
        if pos>0:
            chk_type = value[0:pos].lower()
            chk_value = value[pos+1:]
        else:
            #没有表达式，说明是标签查找
            chk_type = 'label'
            chk_value = value
        if(chk_type=='label'):
            #处理部分匹配的情况，例如待办事项标签后面可能会跟着未读数量，因此，根据*的位置进行部分匹配,出于容错考虑，两端的空格会被忽略
            start_match_flag = end_match_flag = False
            chk_value = chk_value.strip()
            if chk_value[0]=='*':
                end_match_flag = True
                chk_value = chk_value[1:]
            if chk_value[-1]=='*':
                start_match_flag = True
                chk_value = chk_value[0:-1]
            match_flag = (end_match_flag and start_match_flag)
            
            text = node.get_attribute('innerText').strip()
            if match_flag:
                ret = chk_value in text
            elif start_match_flag:
                ret = text.startswith(chk_value)
            elif end_match_flag:
                ret = text.endswith(chk_value)
            else:
                #全文匹配
                ret = chk_value.strip() == node.get_attribute('innerText').strip()
        elif(chk_type=='class'):
            #class有多值，不能简单使用等于
            thisClass = node.get_attribute('class')
            thisClasses = thisClass.split(' ')
            values = value.split(' ')
            ret = True
            for v in values:
                if v !='' and not v in thisClasses:
                    #有一个目标类不存在, 不符合，退出
                    ret = False
                    break
        else:
            #否则，默认检查节点的指定属性
            ret = chk_value.strip() == node.get_attribute(chk_type).strip()
        return ret

class Plug_alert(BaseField):
    f_type='alert'
    def __init__(self,uihandle,element,page="", siteName="",context={}):
        #因为页面代码执行不依赖锚点元素，所以element允许为空
        self.handle=uihandle
        self.page=page
        self.siteName=siteName
        
        self.el_name=element
        self.context=context
        
        #getConfig use the property context,so it must be used at last.
        self.wait_befor_start = self.getConfig('wait_befor_start',default=0.5,toType='float')
        self.try_times = self.getConfig('try_times',default=1,toType='int')
        self.try_interval = self.getConfig('try_interval',default=0,toType='float')
        self.wait=self.getConfig('wait',default=0,toType='float')
        
    def get_alt_obj(self):
        
        #通过text属性检查是否存在对应的有效的对话框
        alt_obj = None
        for i in range(0,self.try_times):
            try:
                alt_obj = self.handle.driver.switch_to_alert()
                alt_obj.text
                break
            except  UnexpectedAlertPresentException as e:
                #一般是alt_obj.text报错，原因未找到,work around it
                for i in range(0,5):
                    try:
                        alt_obj.text
                        break
                    except Exception as e:
                        pass
                break
            except NoAlertPresentException as e:
                sleep(self.try_interval)
                alt_obj=None
            except Exception as e:
                sleep(self.try_interval)
                alt_obj=None
        return alt_obj
    def send(self,value='',context={}):
        sleep(self.wait_befor_start)
        
        alt = self.get_alt_obj()
        
        if not alt:
            raise Exception('not specific alert found ,please check it!')
        if value.lower() in ['ok','accept','confirm','确定','是']:
            alt.accept()
        elif value.lower() in ['cancel','abort','dismiss','放弃','否']:
            alt.dismiss()
        else:
            raise Exception('not valid value found for th alert plugin!,please check it!')
        sleep(self.wait)
        return
