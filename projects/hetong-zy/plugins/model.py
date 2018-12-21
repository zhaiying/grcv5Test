#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-01-15 13:20
# plugins/model.py
from log.log import Logger
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC

import re

from encapsulation.fields import BaseField


# 界面测试组件维护在此--基本界面组件所使用的界面模型
# 包括 ztree,dynamictable,lazytree,ulist等

#以下模型借用了插件的原型，以后也许会独立出来使用自己的基类
#ztree对象
class Model_Ztree(BaseField):
    '''ztree类的原型
    '''
    f_type='Ztree'
    def __init__(self, uihandle, treeName):
        self.handle = uihandle
        self.trees ={}
        id,flag_id = self.getTreeRootId(treeName)
        self.id = id
        if ('cjs' in self.id):
            self.cjs = True
        else:
            self.cjs = False
        
    #获取ztree的标识根节点，作为查找子元素的根起点
    def getTreeRootId(self,treeName):
        uihandle = self.handle
        find_str=treeName.decode(__default_encoding__)
        root = None
        id = ''
        
        max_try = 120
        attemps=max_try
        #uihandle.logger.info('try to find the tree of name:%s' % treeName)
        selector = '#grcsp_select_item_trees div[id^=selectItems_]'
        WebDriverWait(uihandle.driver, 20)
        searchPath = ["css selector",selector]
        
        found = False
        while not found and attemps>0:
            els = uihandle.driver.find_elements(*searchPath)
            found = (len(els)>0)
            attemps = attemps -1
            sleep(1)
        
        if not found:
            raise Exception('can not find the tree("%s--%s") in %i times tries, so stop the testing now!' % (treeName,selector,max_try))
        
        #els = uihandle.driver.find_elements_by_css_selector(selector)
        uihandle.logger.debug('found tree roots, %i matches' % len(els))
        selector_title = '.listTitle'
        for el in els:
            oTitle = el.find_element_by_css_selector(selector_title)
            if(find_str=="" or find_str in oTitle.text):
                print('found the ztree title: %s' % oTitle.text)
                #支持局部匹配
                root = el
                id = el.get_attribute('id')
                flag_el = root.find_element_by_css_selector('li[id^=grcsp_left]')
                flag_id = flag_el.get_attribute('id')
                #找到第一个，就退出循环
                break;
        return id,flag_id
    #点击叶子节点的a链接
    def clickLeaf(self, leaf):
        find_str=leaf.decode(__default_encoding__)
        # 用于ztree-like的叶子节点触发（A链接）
        if(self.cjs):
            id = 'grcsp_left_cjs_deps'
        else:
            id = 'grcsp_left_'
        selector ="#" +self.id+ " li[id^='"+id+"']>a[title='"+find_str+"']"
        #print('selector:%s' % selector)
        link = None
        try:
            #在本选择器中，link可能已经被点击，挪到了右侧区域，所以要处理一下
            #link = self.root.find_element_by_css_selector(selector)
            link = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
            #print('ok')
        except:
            pass
        #print('link type:%s' % type(link))
        if(link!=None):
            self.clickAndScroll(link)
            #link.click()
    #展开父部门分支
    def toggleBranch(self, branch, action='toggle'):
        success=True
        #print('try to expand branch:%s ' % branch)
        find_str=branch.decode(__default_encoding__)
        # 用于ztree-like的干节点展开
        #id = 'grcsp_left_cjs_deps'
        id = 'grcsp_'    #党办文件文书环节，阅知被改成了grcsp_right_notify_sid,所以为了兼容性，改为这样
        xpath="//div[@id='"+self.id+"']//li[contains(@id,'"+id+"')]/a[@title='"+find_str+"']/preceding-sibling::*[1][contains(@id,'_switch')]"
        #xpath="//li[contains(@id,'"+id+"')]/a[@title='"+find_str+"']/preceding-sibling::*[1][contains(@id,'_switch')]"
        #print(xpath)
        #switch = self.root.find_element_by_xpath(xpath)
        switch = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['xpath',xpath]))
        el_class = switch.get_attribute('class')
        #print(el_class)
        if (action=='open'):
            #打开操作，只展开
            if ('_close' in el_class):
                self.expandAndScroll(switch)
            else:
                success=False
        elif(action=='close'):
            #关闭操作，只关闭
            if (not '_close ' in el_class):
                self.expandAndScroll(switch)
            else:
                success=False
        else:
            #否则，切换状态
            self.expandAndScroll(switch)
        return success
   
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def clickAndScroll(self, el):
        #展开部门时，由于人员可能会在显示区域以外，此时，click不会报错，对应的js不会执行（或有效执行），因此，此处通过对点击效果的检查（例如左侧隐藏，右侧显示），来判断是否已经“有效”点击，如果没有，则卷滚后继续点击，直到成功为止
        scrollby = 80 #默认滚动高度
        self.jScroll(0)
        iniStatus = el.is_displayed()
        #print('ini:%s' % iniStatus)
        if (el.is_displayed()):
            el.click()
        else:
            #元素隐藏了，说明已经被选中到右边,目前就这样了，不再继续处理
            pass
        sleep(1)
        #下面先注掉，遇到问题再针对性处理
        '''
        i=0
        scrollTop=0
        scrollLeft=0
        while(el.is_displayed()==iniStatus and i<5):
            #click以后，class没有变化，说明元素不在显示区域，需要滚动对应的div后重新尝试
            #print('no%i:%s' % (i,el.is_displayed()))
            scrollTop=scrollTop+scrollby
            self.jScroll(scrollTop)
            el.click()
            sleep(1)
            i=i+1
        #print('scroll time:%i' % i)
        '''
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def expandAndScroll(self, switch):
        scrollby = 80 #默认滚动高度
        self.jScroll(0)
        iniStatus = switch.get_attribute('class')
        switch.click()
        i=0
        scrollTop=0
        scrollLeft=0
        while(switch.get_attribute('class')==iniStatus and i<5):
            #click以后，class没有变化，说明元素不在显示区域，需要滚动对应的div后重新尝试
            scrollTop=scrollTop+scrollby
            self.jScroll(scrollTop,0)
            sleep(1)
            switch.click()
            i=i+1
        #print('scroll times:%i' % i)
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def jScroll(self, top=0, left=0):
        jscode="t=$('div#"+self.id+" div.left>div.autoOverflow');t.scrollTop(%i);t.scrollLeft(%i);" % (top,left)
        self.handle.driver.execute_script(jscode)
    #从头展开某个部门路径，格式例如'总部/办公厅'，前面的会展开分支，最后一个是点击部门，用于显示部门内容
    def expand(self, treeLinks):
        chains=treeLinks.split('/')
        for i in range(0,len(chains)):
            if (i==len(chains)-1):
                #链条的最后一个是点击叶子节点，用于显示部门内容
                print('leaf:%s clicked' % chains[i].decode(__default_encoding__))
                self.clickLeaf(chains[i])
            else:
                #链条的前面几个会展开分支
                print('branch:%s expanded' % chains[i].decode(__default_encoding__))
                success = self.toggleBranch(chains[i],'open')
                #党办通知中第9环节文书岗处理中，阅知项：政企分公司下有上千人，展开耗时
                sleep(2)
                #if (not success):
                    #break
            sleep(1)
    def expandAll(self, paths):
        #在当前tree上同时展开多个路径
        seperators=','  #支持的分隔符
        list = re.split('['+seperators+']',paths)
        
        #依次选择，由于使用的是ztree变形，人员和部门都在左边，只不过人员是叶子节点，所以使用混合路径展开
        
        for n in list:
            self.expand(n)
            #留出页面节点展开的时间
            sleep(1)
#动态表格对象
class Model_DynamicTable(BaseField):
    '''动态列表的原型
    '''
    f_type='DynamicTable'
    def __init__(self, uihandle, name, rootSelector='.dynamicTable',addButton='动态表格添加按钮'):
        self.handle = uihandle
        self.root = rootSelector
        self.name = name
        self.addButton = addButton
    #打开地址簿窗口
    def add(self):
        btn = self.handle.element('',addButton)
        btn.click()
        sleep(3)
        #self.frame = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['id','selIframe']))
        #self.handle.driver.switch_to_frame(self.frame)
    #关闭地址簿窗口
    def close(self):
        #self.handle.driver.switch_to_default_content()
        quitButton=self.handle.Click("地址簿选择确定按钮")
        sleep(3)
    #处理动态表格的字段填写
    def fields(self,inputs,context={}):
        for f in inputs:
            self.field(f[0],f[1],f[2],context)
#ztree对象
class Model_LazyTree(BaseField):
    '''ztree类的原型,考虑了中移动显示慢的情况，重点加强了等待延时和容器定制
    '''
    f_type='LazyTree'
    def __init__(self, uihandle,treeName, selectors={}, wait=0):
        #selectors{'root','title','cntr','items'}分别是地址树的根节点，标题节点,容器节点，选项节点的css选择器
        #wait，可选参数是为了处理由于候选人太多不能按时加载，增加的延时参数（单位秒），会在根节点找到后，继续延时指定时间，保证地址树能够加载显示完毕。
        self.handle = uihandle
        self.selectors =selectors
        root_id,cntr_id = self.getTreeRootId(treeName)
        self.root_id = root_id
        self.cntr_id = cntr_id
        if(cntr_id==''):
            #容器节点没有id属性，则用根节点来代替（前缀是root|）。
            self.id = root_id
        else:
            self.id = cntr_id
        
        self.type = "simple"
        self.wait = wait
        
    #处理懒加载，高延时的大数据量地址树的展开
    #参数：wait-每次等待时间；max_try-尝试次数；min_required-至少要获取多少子元素才算加载完成；wait_for_complete-完成前需要额外等待多少时间
    def __findElements_by_xpath(self,cntr,sub_selector,wait=1,max_try=120,min_required=1,wait_for_complete=2):
        return self.__findElements(cntr,'xpath',sub_selector,wait,max_try,min_required,wait_for_complete)
    #参数：wait-每次等待时间；max_try-尝试次数；min_required-至少要获取多少子元素才算加载完成；wait_for_complete-完成前需要额外等待多少时间
    def __findElements_by_css_selector(self,cntr,sub_selector,wait=1,max_try=120,min_required=1,wait_for_complete=2):
        return self.__findElements(cntr,'css selector',sub_selector,wait,max_try,min_required,wait_for_complete)
    
    #参数：wait-每次等待时间；max_try-尝试次数；min_required-至少要获取多少子元素才算加载完成；wait_for_complete-完成前需要额外等待多少时间
    def __findElements(self,cntr,selector_type,sub_selector,wait=1,max_try=120,min_required=1,wait_for_complete=2):
        uihandle = self.handle
        
        attemps=max_try
        #通过尝试获取子元素来判断懒加载是否完成
        searchPath = [selector_type,sub_selector]
        
        found = False
        while not found and attemps>0:
            els = cntr.find_elements(*searchPath)
            found = (len(els)>=min_required)
            attemps = attemps -1
            sleep(wait)
        
        if not found:
            #延时后仍未找到指定根节点，抛异常退出
            raise Exception('can not find the tree("%s--%s") in %i times tries, so stop the testing now!' % (treeName,selector,max_try))
        else:
            #为保险起见，额外等待时间
            sleep(wait_for_complete)
        return els
        
    #获取地址树结构的标识根节点，作为查找子元素的根起点
    def getTreeRootId(self,treeName):
        uihandle = self.handle
        find_str=treeName.decode(__default_encoding__)
        root = None
        id = ''
        
        #查找根节点，并进行适当等待，直到根节点找到为止
        selector_root = self.selectors['root']
        els = self.__findElements_by_css_selector(uihandle.driver,selector_root)
        '''
        max_try = 120
        attemps=max_try
        #uihandle.logger.info('try to find the tree of name:%s' % treeName)
        WebDriverWait(uihandle.driver, 20)
        searchPath = ["css selector",selector_root]
        
        found = False
        while not found and attemps>0:
            els = uihandle.driver.find_elements(*searchPath)
            found = (len(els)>0)
            attemps = attemps -1
            sleep(1)
        
        #延时后仍未找到指定根节点，抛异常退出
        if not found:
            raise Exception('can not find the tree("%s--%s") in %i times tries, so stop the testing now!' % (treeName,selector,max_try))
        '''
        
        #可能存在多个满足条件的根节点，那么根据标题筛选出需要的那个
        uihandle.logger.debug('found tree roots, %i matches' % len(els))
        selector_title = self.selectors['title']
        selector_cntr = self.selectors['cntr']
        i=0
        root_id=""
        cntr_id=""
        for el in els:
            #标题节点
            oTitle = el.find_element_by_css_selector(selector_title)
            if(find_str=="" or find_str in oTitle.text):
                print('found the ztree title: %s' % oTitle.text)
                #支持局部匹配
                root = el
                root_id = el.get_attribute('id')
                
                cntr = root.find_element_by_css_selector(selector_cntr)
                cntr_id = cntr.get_attribute('id')
                
                #找到第一个，就退出循环
                break;
            i = i+1
        if root_id=="" and cntr_id=="":
            raise Exception('cannot get the id of addresstree, please contact you testing supportor')
        return root_id,cntr_id
    #点击叶子节点的a链接
    def clickLeaf(self, leaf):
        find_str=leaf.decode(__default_encoding__)
        # 用于ztree-like的叶子节点触发（A链接）
        selector ="#" +self.id+ " li[id^='"+self.id+"']>a[title='"+find_str+"']"
        #print('selector:%s' % selector)
        link = None
        try:
            #在本选择器中，link可能已经被点击，挪到了右侧区域，所以要处理一下
            #link = self.root.find_element_by_css_selector(selector)
            link = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
            #print('ok')
        except:
            pass
        #print('link type:%s' % type(link))
        if(link!=None):
            if (link.is_displayed()):
                link.click()
            else:
                #元素隐藏了，说明已经被选中到右边,目前就这样了，不再继续处理
                pass
            #self.clickAndScroll(link)
            #link.click()
    #展开父部门分支
    def toggleBranch(self, branch, action='toggle'):
        success=True
        #print('try to expand branch:%s ' % branch)
        find_str=branch.decode(__default_encoding__)
        # 用于ztree-like的干节点展开
        
        #id = 'grcsp_left_cjs_deps'
        #id = 'grcsp_'  
        
        #获取部门展开手柄
        xpath="//*[@id='"+self.id+"']//li[@id]/a[@title='"+find_str+"']/preceding-sibling::*[1][contains(@id,'_switch')]"
        
        #print(xpath)
        #处理懒加载
        switch = self.__findElements_by_xpath(self.handle.driver,xpath)[0]
        #switch = self.root.find_element_by_xpath(xpath)
        #switch = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['xpath',xpath]))
        
        target_id = switch.get_attribute('id')
        
        #将对应的节点移动到显示区域，以便展开（实测，如果不在显示区域，点击不报错，但也不会展开）
        self.targetScroll(self.cntr_id,target_id)
        
        el_class = switch.get_attribute('class')
        #print(el_class)
        if (action=='open'):
            #打开操作，只展开
            if ('_close' in el_class):
                self.expandAndWait(switch)
            else:
                success=False
        elif(action=='close'):
            #关闭操作，只关闭
            if (not '_close ' in el_class):
                self.expandAndWait(switch)
            else:
                success=False
        else:
            #否则，切换状态
            self.expandAndWait(switch)
        return success
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def expandAndWait(self, switch, max_try=120, wait=1,retry=2):
        #增加了对等待图标的检测，如果等待图标消失，还没展开，则直接结束，重新访问
        switch_id = switch.get_attribute('id')
        ico_id = switch_id.replace('_switch','_ico')
        ico = self.handle.driver.find_element_by_id(ico_id)
        iniStatus = switch.get_attribute('class')
        icoStatus = ico.get_attribute('class')
        switch.click()
        i=0
        completed = False
        loading = False
        ready = False
        while(not completed and i<max_try):
            #click以后，class没有变化，说明需要等待展开（即ajax异步加载完成）
            i=i+1
            if i%10==0:
                print('scroll times:%i \r' % i),
            sleep(wait)
            #检测
            tempico = ico.get_attribute('class')
            if (not loading and '_loading' in tempico):
                #检测到加载等待图标
                loading = True
                
            if (loading and '_loading' not in tempico):
                #从加载等待状态退出
                loading = False
                ready = True
                #print("no.%i:%s" % (i,tempico))
                icoStatus = tempico
            completed = (switch.get_attribute('class')!=iniStatus)
            
            if (ready and not completed):
                #异常情况，等待已经结束，但是没有展开，例如中移动的党委会议纪要的参与人首次打开的情况，那么再处理一下(尝试数retry减一)
                if retry >0:
                    print('fail to expand ,try time left %i' % retry-1)
                    self.expandAndWait(switch,max_try,wait,retry-1)
                else:
                    #重试结束，抛异常退出
                    raise Exception('Fail to expand the lazytree finally , please reporte to your supportor')
                
        return completed
    #用于检查在异步加载的情况下，指定的异步子元素是否存在（加载完成或达到指定的个数）
    #参数：wait-每次轮询等待时间；max_try-尝试次数；min_required-至少要获取多少子元素才算加载完成；wait_for_complete-完成前需要额外等待多少时间
    def waitForReady(self,cntr,selector_type,sub_selector,wait=1,max_try=240,min_required=1,wait_for_complete=1):
        els = self.__findElements(cntr,selector_type,sub_selector,wait,max_try,min_required,wait_for_complete)
        return (len(els)>=min_required)
        
    def ready(self):
        cntr = self.handle.driver.find_element_by_id(self.id)
        success=self.waitForReady(cntr,'css selector',self.selectors['items'],wait=1,max_try=240,min_required=1,wait_for_complete=1)
        return success
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效(将目标元素，移到中央位置)
    def targetScroll(self, baseId, targetId):
        jscode = "!function(){base = $('#"+baseId+"');base.scrollTop(0);t=$('#"+targetId+"');scrollY=t.offset().top-(base.offset().top+base.height()/2-t.height()/2);base.scrollTop(scrollY);}()"
        self.handle.driver.execute_script(jscode)
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def jScroll(self, top=0, left=0):
        jscode="t=$('#"+self.id+"');t.scrollTop(%i);t.scrollLeft(%i);" % (top,left)
        self.handle.driver.execute_script(jscode)
    #从头展开某个部门路径，格式例如'总部/办公厅'，前面的会展开分支，最后一个是点击部门，用于显示部门内容
    def expand(self, treeLinks):
        chains=treeLinks.split('/')
        for i in range(0,len(chains)):
            if (i==len(chains)-1):
                #链条的最后一个是点击叶子节点，用于显示部门内容
                print('leaf:%s clicked' % chains[i].decode(__default_encoding__))
                self.clickLeaf(chains[i])
            else:
                #链条的前面几个会展开分支
                print('branch:%s expanded' % chains[i].decode(__default_encoding__))
                success = self.toggleBranch(chains[i],'open')
                #党办通知中第9环节文书岗处理中，阅知项：政企分公司下有上千人，展开耗时
                sleep(2)
                #if (not success):
                    #break
            sleep(1)
    def expandAll(self, paths):
        #在当前tree上同时展开多个路径
        seperators=','  #支持的分隔符
        list = re.split('['+seperators+']',paths)
        
        #依次选择，由于使用的是ztree变形，人员和部门都在左边，只不过人员是叶子节点，所以使用混合路径展开
        
        for n in list:
            self.expand(n)
            #留出页面节点展开的时间
            sleep(1+self.wait)

#ul列表对象
class Model_Ulist(BaseField):
    '''ul list类的原型，用于非ztree的简单选择框，使用ul list，一般是单层选择
    '''
    f_type='Ulist'
    def __init__(self, uihandle, listName):
        self.handle = uihandle
        self.trees ={}
        id = self.getRootId(listName)
        self.id = id
    #获取ul list的标识根节点，作为查找子元素的根起点
    def getRootId(self,listName):
        uihandle = self.handle
        find_str=listName.decode(__default_encoding__)
        root = None
        id = ''
        
        print('listName:%s' % listName.decode(__default_encoding__))
        #先找外层td
        selector = '#GEditModal .maintable .col-md-1'
        WebDriverWait(uihandle.driver, 20)
        searchPath = ["css selector",selector]
        els = uihandle.driver.find_elements(*searchPath)
        
        #再找内层的列表，检查标题，看哪个列表是所需列表
        for el in els:
            id = self.getInnerId(el,find_str)
            if id!='':
                #成功获得第一个满足条件的列表的id，则结束递归
                break;
        return id
    #需要支持列表的嵌套，处理列表的递归查询
    def getInnerId(self,topElement,find_str):
        id = '' #返回值
        selector_title = 'span'
        selector_container = 'table tr'
        oCntrs = topElement.find_elements_by_css_selector(selector_container)
        if(len(oCntrs)==0):
            #不存在子容器，直接处理
            oTitle = topElement.find_element_by_css_selector(selector_title)
            #print('inner title:%s' % oTitle.text)
            if(find_str=="" or find_str in oTitle.text):
                print('found:%s' % oTitle.text)
                #支持局部匹配
                root = topElement.find_element_by_css_selector('ul[id]')
                id = root.get_attribute('id')
        else:
            #存在子容器，递归处理
            for el in oCntrs:
                id = self.getInnerId(el,find_str)
                #print('getInnerId:%s' % id)
                if id!='':
                    #成功获得对应列表的id，则结束递归
                    break
        return id    
                                                                                                                            
    #点击列表的指定名称的节点，支持局部匹配，找到第一个为止
    def click(self,text):
        uihandle = self.handle
        find_str=text.decode(__default_encoding__)

        #找到对应的容器ul
        WebDriverWait(uihandle.driver, 20)
        root = uihandle.driver.find_element_by_id(self.id)
        
        els = root.find_elements_by_css_selector('li[title]')
        for el in els:
            label = el.text
            if(find_str=="" or find_str in label):
                print('found:%s' % label)
                el.click()
                #找到第一个，就退出循环
                break;

#系统菜单对象
class Model_SysMenu(BaseField):
    '''系统菜单类型
    特点是 每一级菜单是li>a>span.title结构
    '''
    f_type='SysMenu_Base'
    def __init__(self, uihandle, element='系统主导航菜单',context={}):
        self.handle = uihandle
        self.el_name = element
        self.context=context
    def send(self,menus):
        if(menus==""):
            return
        seperator='/'
        #root = self.handle.driver.find_element_by_css_selector('ul.page-sidebar-menu')
        
        root = self.handle.element('',self.el_name)
        self.click(root,menus)
    def click(self,cntr_node,menus):
        found = False
        if(menus==""):
            #the sub-menus is empty, so all the menus have been found 
            return True
        seperator='/'
        menus_a = menus.split(seperator)
        label=menus_a[0]
        nodes = cntr_node.find_elements_by_css_selector('li')
        #ul.page-sidebar-menu>li>a>span.title
        for i in range(0,len(nodes)):
            titles=nodes[i].get_attribute('innerText').split('\n')
            if label.decode(__default_encoding__) == titles[0].strip():
                #found the path, recurse now
                menu_sub='/'.join(menus_a[1:])
                if(menu_sub==""):
                    found = True
                    #click the leaf node
                    t=nodes[i].find_element_by_css_selector('a')
                    t.click()
                    sleep(1)
                    break
                else:
                    # the branch node only clicked when not open
                    if 'open' not in nodes[i].get_attribute('class'):
                        t=nodes[i].find_element_by_css_selector('a')
                        t.click()
                        sleep(1)
                    cntr_sub=nodes[i].find_elements_by_css_selector('ul')
                    if(len(cntr_sub)>0):
                        sub_found = self.click(cntr_sub[0],menu_sub)
                        if(sub_found==True):
                            found = True
                            break
        return found
#标准ztree对象  
class Model_Standard_Ztree(BaseField):
    '''ztree类的原型
    '''
    f_type='Ztree_Base'
    def __init__(self, uihandle, element, context={}):
        #与界面组件不同，模型element是ztree的根元素
        self.handle = uihandle
        self.el_name = element
        self.context=context
        
        #选择模式：click和check
        self.select_mode = self.getConfig('select_mode',default='click',toType='str')
        #需要使用的按钮定义初始化
        self.btn_open = self.getConfig('btn_open',default='',toType='str')
        
        self.btn_ok = self.getConfig('btn_ok',default='',toType='str')
        self.btn_cancel = self.getConfig('btn_cancel',default='',toType='str')
        self.btn_left = self.getConfig('btn_left',default='',toType='str')
        self.btn_right = self.getConfig('btn_right',default='',toType='str')
        self.btn_all_left = self.getConfig('btn_all_left',default='',toType='str')
        self.btn_all_right = self.getConfig('btn_all_right',default='',toType='str')
        self.wait_after_open = self.getConfig('wait_after_open',default=0.5,toType='float')
        self.wait_after_select = self.getConfig('wait_after_select',default=0.5,toType='float')
        self.wait_after_close = self.getConfig('wait_after_close',default=0,toType='float')
        #卷滚容器锚设置
        self.cntr_scroll = self.getConfig('cntr_scroll',default='',toType='str')
    def send(self,menus):
        if(menus==""):
            return
        
        root = self.getElement(self.el_name)
        #处理多选参数
        seperators=',;'  #支持的分隔符
        mylist = re.split('['+seperators+']',menus)
        
        #依次选择，使用的是ztree变形
        for menu in mylist:
            self.click(root,menu)
        if self.select_mode.lower()!='double_click':
            #如果不使用双击，需要考虑是否使用向右箭头
            if(len(mylist))==1:
                #单选，最后可能需要触发单右移
                if(self.btn_right!=''):
                    #如果传递了右选按钮，说明还需要点击右选才能移入右侧
                    btn = self.getElement(self.btn_right)
                    btn.click()
            if(len(mylist))>1:
                #多选，最后可能需要触发多项右移
                if(self.btn_all_right!=''):
                    #如果传递了右选按钮，说明还需要点击右选才能移入右侧
                    btn = self.getElement(self.btn_all_right)
                    btn.click()
        
    def clickNode(self,node,mode="click"):
        #处理ztree过长，超出容器显示区域导致的无法“有效”点击的问题
        if self.cntr_scroll!='':
            #存在卷滚参数，则先卷滚至合适位置
            target_id = node.get_attribute('id')
        
            #将对应的节点移动到显示区域，以便展开（实测，如果不在显示区域，点击不报错，但也不会展开）
            self.targetScroll(self.cntr_scroll,"#"+target_id)
        
        if mode=="double_click":
            self.handle.doubleClick(node)
        else:
            node.click()

    def click(self,cntr_node,menus):
        
        found = False
        if(menus==""):
            #the sub-menus is empty, so all the menus have been found 
            return True
        seperator='/'
        menus_a = menus.split(seperator)
        label=menus_a[0]
        nodes = cntr_node.find_elements_by_css_selector('li')
        #ul.page-sidebar-menu>li>a>span.title
        for i in range(0,len(nodes)):
            node = nodes[i]
            id = node.get_attribute('id')
            titles=node.get_attribute('innerText').split('\n')
            if label.decode(__default_encoding__) == titles[0].strip():
                #found the path, recurse now
                menu_sub='/'.join(menus_a[1:])
                if(menu_sub==""):
                    found = True
                    if self.select_mode.lower()=='check':
                        # check the checkbox for select
                        
                        t=node.find_element_by_css_selector('span[id=%s_check]' % id)
                        style_cls = t.get_attribute('class').lower()
                        if not '_true' in style_cls:
                            self.clickNode(t)
                    elif self.select_mode.lower()=='double_click':
                        #click the leaf node
                        t=node.find_element_by_css_selector('a[id=%s_a]' % id)
                        self.clickNode(t,mode='double_click')
                    else:
                        #click the leaf node
                        t=node.find_element_by_css_selector('a[id=%s_a]' % id)
                        self.clickNode(t)
                    sleep(1)
                    break
                else:
                    # the branch node only clicked when not open
                    switch=node.find_element_by_css_selector('span[id=%s_switch]' % id)
                    if 'open' not in switch.get_attribute('class'):
                        self.clickNode(switch)
                        sleep(1)
                    cntr_sub=node.find_elements_by_css_selector('ul[id=%s_ul]' % id)
                    if(len(cntr_sub)>0):
                        sub_found = self.click(cntr_sub[0],menu_sub)
                        if(sub_found==True):
                            found = True
                            break
        
        if not found:
            print('tree node(%s) not found, raise error' % menus)
            raise Exception('tree node(%s) not found, raise error' % menus)
        sleep(self.wait_after_select)
        return found
        
    #打开地址簿窗口
    def open(self):
        
        btn = self.getElement(self.btn_open)
        btn.click()
        #wait some time for some slow loading conditions
        sleep(self.wait_after_open)
    #保存关闭地址簿窗口
    def ok(self):
        btn = self.getElement(self.btn_ok)
        btn.click()
        sleep(self.wait_after_close)
    def cancel(self):
        btn = self.getElement(self.btn_cancel)
        btn.click()
        sleep(self.wait_after_close)
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效(将目标元素，移到中央位置)
    def targetScroll(self, baseAnchor, targetAnchor):
        jscode = "!function(baseAnchor,targetAnchor){base = $(baseAnchor);base[0].scrollTop=0;t=$(targetAnchor);scrollY=t.offset().top+t.height()-(base.offset().top+base.height());base[0].scrollTop=scrollY;}('"+baseAnchor+"','"+targetAnchor+"')"
        self.handle.driver.execute_script(jscode)
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def jScroll(self, top=0, left=0):
        jscode="t=$('#"+self.id+"');t.scrollTop(%i);t.scrollLeft(%i);" % (top,left)
        self.handle.driver.execute_script(jscode)

class Model_View_Panel(BaseField):
    '''视图类的原型
    '''
    f_type='model_view_panel'
    
    def __init__(self, handle, element,page="", siteName="",context={}):
        self.handle = handle
        el = uihandle.element(page, element, siteName,context=context)
        self.el=el
        self.el_name=element
        self.viewname = element
        self.context = context
        #self.tabs,self.activeTabIndex = self.__getTabs__()
        #self.checkSelector = checkSelector
        self.selector_check = self.getConfig('selector_check',default='',toType='str')

    
    #检查视图是否加载完成
    def ready(self,delay=5,count=20):
        driver = self.handle.driver
        ready = False
        count = 30
        delay = 2
        
        while not ready and count>0:
            count=count-1
            try:
                tbl = driver.find_element_by_css_selector(self.checkSelector)
            except:
                sleep(delay)
                continue
            #todo容器没问题了，但还要检查视图内容是否出现
            try:
                trs = tbl.find_elements_by_tag_name('tr')
            except:
                sleep(delay)
                continue
            if (len(trs)>0):
                #有内容了，退出等待循环，设置成功标志
                ready=True
        return ready
        
    #触发视图操作（为方便，输入操作的部分文本即可，有多个匹配，触发第一个）,可用于翻页等视图操作
    def clickAction(self, label):
        actions = []
        els = self.handle.elements('', '待办视图操作','')
        i=0
        label=label.decode(__default_encoding__)
        found = False
        for l in els:
            if(label in l.text):
                c = l.get_attribute('class')
                if (not 'disabled' in c ):
                    l.click()
                    sleep(1)
                    found = True
                else:
                    print('the action(%s) had already been disbled, so ignore it' % label.decode(__default_encoding__))
            i=i+1
        if not found:
            print('the action(%s) does no exist, so ignore it' % label.decode(__default_encoding__))
        return found
    #从页面获取所有视图页签名称，返回数组
    
    def isDocInView(self,docTitle,max_try=10):
        for i in range(0,max_try-1):
            rowNum = self.handle.findRowInTable('公文视图',docTitle)
            found = (rowNum>-1)
            if (found):
                return True
            else:
                #尝试翻页以后再检查
                self.clickAction('下一页')
        #没有找到，返回False
        return False
    
    def open_doc(self,docTitle,max_try=10):
        print(('扩展：在视图（%s）中打开文档(%s)' % (self.viewname,docTitle)).decode(__default_encoding__))

        for i in range(0,max_try-1):
            try:
                print(i)
                success = self.handle.tableRowClick(self.viewname,docTitle)
            except:
                #found but failure in clicking the element
                raise Exception('some error occurrs while clicking document(%s) in View(%s)' % (docTitle,self.viewname))

            if (success):
                sleep(5)
                return True
            else:
                #尝试翻页以后再检查
                next_found = self.clickAction('下一页')
                sleep(3)
                if (not next_found or i==max_try-1):
                    #下一页按钮没找到，或禁用了，则终止翻页处理
                    print('The doc(%s) is not found in view(%s) after (%i) tries' % (docTitle.decode(__default_encoding__),self.viewname.decode(__default_encoding__),i+1))
                    break
        sleep(1)
        return False
        
    def check(self):
        pass
        

class Model_table(BaseField):
    '''视图列表的原型
    '''
    f_type='model_table'
    def __init__(self, handle, element,page="", siteName="",context={},parent=None):
        self.handle = handle
        el = self.handle.element(page, element, siteName,context=context)
        self.el=el
        self.el_name=element
        self.viewname = element
        self.context = context
        self.parent = parent
        self.selectMode = self.getConfig('select_mode',default='',toType='str')
        self.clickMode = self.getConfig('click_mode',default='',toType='str').lower().strip()
        self.action_col = self.getConfig('action_col',default=0,toType='int')
    def nav_next(self,page_num):
        if self.parent==None:
            return -1
        return self.parent.nav(pag_num)
        
    def getRow(self,condition):
        
        lists=self.el.find_elements_by_tag_name('tr')
        seq=0
        for l in lists:
            #print(l.text)
            t=l.find_elements_by_tag_name('td')
            if len(t)>0 and self.chkCondition(l,condition,seq=seq):
                return l
            seq=seq+1
        return None
        
    def clickRow(self,condition,click_mode='click'):
        success=False
        dbl_settings = ['double','dbl','doubleclick','dblclick','double_click']
        rowItem = self.getRow(condition)
        if not rowItem:
            #没找到指定的列，返回false
            return False
        
        #先检查是否包括a标签
        children = rowItem.find_elements_by_tag_name('a')
        if len(children)>0:
            children[0].click()
            success = True
        else:
            #否则逐列尝试点击
            children = rowItem.find_elements_by_tag_name('td')
            
            for el in children:
                try:
                    if self.clickMode in dbl_settings or click_mode in dbl_settings:
                        self.handle.doubleClick(el)
                    else:
                        #默认单击
                        el.click()
                    success=True
                    break
                except:
                    pass
        if not success:
            raise Exception('some error occurrs while clicking elemnt(%s)' % condition)
        return success
    def unselectRow(self,condition,context={}):
        self.selectRow(condition,force='unselect')
    def selectRow(self,condition,force='select',context={}):
        success=False
        #支持直接传元素处理，增加判断
        if type(condition)==str:
            rowItem = self.getRow(condition)
        else:
            rowItem = condition
        if self.selectMode=="check":
            check_els = rowItem.find_elements_by_css_selector('input[type=checkbox]')
            if len(check_els)>0:
                ck_el=check_els[0]
                if (force.lower()!='unselect'):
                    #force select
                    if not ck_el.is_selected():
                        ck_el.click()
                else:
                    #force unselect
                    if ck_el.is_selected():
                        ck_el.click()
                success=True
            else:
                #no checkbox was found, so try click once instead or should be modified later
                children = rowItem.find_elements_by_tag_name('td')
                for el in children:
                    try:
                        el.click()
                        success=True
                        break
                    except:
                        pass
        else:
            children = rowItem.find_elements_by_tag_name('td')
            for el in children:
                try:
                    el.click()
                    success=True
                    break
                except:
                    pass
            
        if not success:
            raise Exception('some error occurrs while selecting elemnt(%s)' % condition)
        return success
    def hasRow(self,condition):
        rowItem = self.getRow(condition)
        return rowItem!=None
        
    def chkCondition(self,el,condition,seq=0):
        item = condition.strip()
        pos = item.find('=')
        if pos>0:
            it=item[:pos]
            v=item[pos+1:]
        else:
            it='text'
            v=item
        if item=='id':
            return (v.decode(__default_encoding__) in el.get_attribute('id'))
        elif item=='seq':
            return seq==int(v)
        else:
            return (v.decode(__default_encoding__) in el.get_attribute('innerText'))

        
        
