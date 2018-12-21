#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-08-15 13:20
# encapsulation/smartdotoa.py


#pdb.set_trace()
# 用于测试慧点oa的封装部分维护在此
#from config.FlowConfig import *
from config import currentProject
from encapsulation.plugins import *
SmartFlow=currentProject.innerload('ext.flowconfig.SmartFlow')

#from config.FlowConfigExt_mobile_uat import *
from log.log import Logger
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC

import re

import win32api
import win32gui
import win32con


from encapsulation.encapsulation import UIHandle

'''
    查找元素的关键字，用于ini文件中的设置

    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"
'''

class SmartHandle(UIHandle):
    # 构造方法，用来接收selenium的driver对象
    @classmethod
    def __init__(self):
        UIHandle.__init__()
    @classmethod
    def init(cls, driver):
        UIHandle.init(driver)
        
        cls.addressbook={}
        cls.actionPanel=ActionPanel(cls)
        cls.menu=Menu(cls)
        
    #处理表单字段额外参数,由于之前json包在转换中会遇到编码问题，因此手动处理，格式例如idx:1;wait:3
    @classmethod
    def extraParams(self,str):
        str=str.strip()
        if(str==""):
            return {}
        p={}
        arr = str.split(',')
        for i in arr:
            a = i.split('=')
            if(len(a)>1):
                p[a[0]]=a[1]
        return p
        
    #处理表单字段(输入为数组)
    
    def fields(self,inputs,context={},skip_empty_field=False):
        for f in inputs:
            
            element = f[0]
            value = f[1]
            
            if(len(f)>3):
                parameters = f[3]
            else:
                parameters = ''
            f_extra = self.siteConfig.getElementExtraInfos(self.currentSite,element,context=context)
            f_type = self.siteConfig.getExtraInfo(f_extra,'ftype','input',toType='str')
            
            #合并参数，根据决策延迟的原理,利用业务设置excel中的参数（用例配置时）覆盖调用程序传参（用例设计时）
            p = self.extraParams(parameters)
            c = dict(context,**p)
            
            self.field(element,value,f_type,context=c,skip_empty_field=skip_empty_field)
    
    #处理表单字段
    
    def field(self,element,value,type='input',context={},skip_empty_field=False):
        #锚点设置ini中的参数
        if element!='':
            #element为空，说明是代码直接调用，没有对应的ini设置，例如ext_actions（流程的其他参数扩展）
            f_extra = self.siteConfig.getElementExtraInfos(self.currentSite,element,context=context)
        else:
            f_extra = {}
        #合并参数，根据决策延迟的原理,利用运行时的流程变量覆盖业务设置excel中的参数（用例配置或设计时）覆盖锚点设置ini的参数传参（用例设计时）
        c = dict(f_extra,**context)
        c = dict(c,**(self.system_context))
        
        value = self.compute(value,c)
            
        #pdb.set_trace()
        cls = smartPlugin(type)
        if (cls!=None):
        
            #检查空值是否需要跳过执行
            if not hasattr(cls,'must_have_value') or cls.must_have_value:
                #如果该插件必须要参数，那么skip_empty_field参数将会生效，跳过那些故意设置成空的插件实例，例如意见框，为空，表示不需要处理该插件
                if skip_empty_field and not value:
                    return
            
            field=cls(self,element,context=c)
            field.send(value,context=c)
        else:
            raise Exception('Field plugin type(%s) not found, please checkit ' % type)
        '''
        下列延时代码，因为已经在各组件中处理，所以注释掉
        try:
            #如果正确设置了等待参数，那么进行相应的延时
            t=int(context['wait'])
            sleep(t)
            print('字段（%s）填写后延时%i秒'.decode(__default_encoding__) % (element.decode(__default_encoding__),t))
        except:
            #否则默认延时0.1秒
            sleep(0.1)
        '''
    #获取实例流程中指定的表单内容
    def getForm(self,form_name,skip_empty_form=False):
        #skip_empty_form标记表示会检查指定表单是否存在，如果不存在，返回None，而不是抛异常
        form = None
        if self.cur_node and self.cur_node.workflow:
            try:
                form = self.cur_node.workflow.getForm(form_name)
            except Exception as e:
                if type(form_name)==str:
                    u_form = form_name.decode(__default_encoding__)
                else:
                    u_form = form_name
                print ('=====warnning: The specified form(%s) setting does not exists!' % u_form)
                if not skip_empty_form:
                    raise e
        else:
            raise Exception('error in getting workflow setting while processing the specified form(%s)' % form_name)
        return form
    #执行实例流程中指定的表单
    def fillForm(self,form_name,context={},skip_empty_field=False,skip_empty_form=False):
        #check_is_exist标记表示会检查指定表单是否存在，如果不存在，则跳过该表单，而不是抛异常
        #由于之前的fillform可能会执行全局变量的修改，所以此处需要使用全局变量重新覆盖刷新
        global_context = self.system_context
        context = dict(context,**global_context)
        
        form = self.getForm(form_name, skip_empty_form=skip_empty_form)
        if form:
            self.fields(form.formInputs(),context,skip_empty_field=skip_empty_field)
        
    @classmethod    
    def assignee(self,personList):
        panel=self.actionPanel
        panel.setAssignee(personList)
    @classmethod    
    def setOpinion(self,opinion):
        panel=self.actionPanel
        panel.setOpinion(opinion)
    @classmethod    
    def selectTransition(self,transition):
        panel=self.actionPanel
        panel.selectTransition(transition)
    @classmethod    
    def submitOpinion(self):
        panel=self.actionPanel
        panel.submitOpinion()
    @classmethod    
    def clickMenu(self,menus):
        menu=self.menu
        menu.click(menus)
    @classmethod    
    def setArchive(self,option):
        panel=self.actionPanel
        panel.setArchive(option)

 
    
class ActionPanel():
    # 构造方法，用来接收selenium调用所需的对象
    @classmethod
    def __init__(self, handle):
        self.handle = handle
        self.checklist={}
        self.initialized = False
    # 填写归档选项
    @classmethod
    def setArchive(self,option):
        #试图设置归档选项
        options=['永久','长期','短期','临时']
        if (option=="" or not option in options):  #为空，或非法数值，则不处理
            return
            
        #归档类型选择
        els = self.handle.elements("","归档选项")
        label=option.decode(__default_encoding__)
        for l in els:
            #print('label:%s vs %s' % (label,l.text))
            if(label in l.text):
                el=l.find_element_by_tag_name('input')
                el.click()
        sleep(0.5)
    # 填写意见
    @classmethod
    def setOpinion(self,opinion):
        options=['同意。','不同意。','其它']
        if (opinion==""):  #为空，则不处理
            return
        seperators='|'  #支持的分隔符
        list = re.split('['+seperators+']',opinion)
        
        if(list[0] in options):
            radio = list[0]
            if(len(list)>1):
                opinion = list[1]
            else:
                opinion = ""
        else:
            #没有参数，说明不是决策性意见
            radio = ''
            opinion = list[-1]
            
        #意见输入
        
        if(opinion!=''):
            self.handle.Input("意见框",opinion)
        #意见类型选择
        if radio!='':
            els = self.handle.elements("","意见选项")
            #决策意见，需要进行选择
            for l in els:
                label=radio.decode(__default_encoding__)
                
                if(label == l.text):
                    el=l.find_element_by_tag_name('input')
                    el.click()
        sleep(0.5)

    # 公文意见和分支区域的提交
    @classmethod
    def submitOpinion(self):
        label = '提交'.decode(__default_encoding__)
        region=self.handle.driver.find_element_by_css_selector('#grcspSubmitWindow')
        els = region.find_elements_by_css_selector('div.modal-footer>button')
        for l in els:
            if(label in l.text):
                l.click()

        sleep(1)
        
    # 设置（修改）处理人，样例（'范宁,宋金超'）
    @classmethod
    def setAssignee(self,nameList):
        #统一添加延时，避免加载缓慢引起ztree.getTreeRootId方法报错
        sleep(1)
        multiPrefix='multi|'
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        if(nameList.startswith(multiPrefix)):
            #标识是4会签框格式类似'主办:张三,李四;协办:王五'，会自动在“主办”中选择张三和李四，“协办”选择王五
            cjsList = nameList[len(multiPrefix):].split(';') #分号分隔不同的会签区段
            #多会签显示更慢，需要多等一会
            sleep(1)
            for c in cjsList:
               self.selectSingleTree(c)
        else:
            self.selectSingleTree(nameList)
        sleep(2)
    # 设置处理人，样例（'部门1/范宁,部门2/宋金超'）
    @classmethod
    def selectSingleTree(self,nameList):
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        if(nameList.find(':')>=0):
            #页面上存在多个ztree选择器，需要分别选择，格式类似'主办:部门1/张三,部门2李四'，会自动在“主办”中选择张三和李四
            r = nameList.split(':')
            region = r[0]
            nList = r[1]
        else:
            #页面上只存在一个ztree选择器，就不区分了，简化接口
            region = ""
            nList = nameList
        
            
        ztree = Model_Ztree(self.handle,region)
        ztree.expandAll(nList)
    '''        
    # 设置（会签）处理人，样例（'范宁,宋金超'）
    @classmethod
    def setCjsAssignee(self,nameList):
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        seperators=',;'  #支持的分隔符
        list = re.split('['+seperators+']',nameList)

        #依次选择，由于使用的是ztree变形，人员和部门都在左边，只不过人员是叶子节点，所以使用混合路径展开
        
        for n in list:
            root = self.getZtreeRoot(n)
            self.expandZtrees(root,n)
            #留出页面节点展开的时间
            sleep(1)
        sleep(2)
    '''
    '''
    #点击叶子节点的a链接
    @classmethod    
    def clickLeaf(self, leaf):
        find_str=leaf.decode(__default_encoding__)
        # 用于ztree-like的叶子节点触发（A链接）
        if(self.cjs):
            id = 'grcsp_left_cjs_deps'
        else:
            id = 'grcsp_left_'
        selector = "li[id^='"+id+"']>a[title='"+find_str+"']"
        #print('selector:%s' % selector)
        link = None
        try:
            #在本选择器中，link可能已经被点击，挪到了右侧区域，所以要处理一下
            link = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
            #print('ok')
        except:
            pass
        #print('link type:%s' % type(link))
        if(link!=None):
            link.click()
    '''
    '''
    #展开父部门分支
    @classmethod    
    def toggleBranch(self, branch, action='toggle'):
        success=True
        print('try to expand branch:%s ' % branch)
        find_str=branch.decode(__default_encoding__)
        # 用于ztree-like的干节点展开
        id = 'grcsp_left_cjs_deps'
        xpath="//li[contains(@id,'"+id+"')]/a[@title='"+find_str+"']/preceding-sibling::*[1][contains(@id,'_switch')]"
        #print(xpath)
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
    @classmethod    
    def expandAndScroll(self, switch):
        scrollby = 180 #默认滚动高度
        self.jScroll(0)
        iniClass = switch.get_attribute('class')
        switch.click()
        i=0
        scrollTop=0
        while(switch.get_attribute('class')==iniClass and i<5):
            #click以后，class没有变化，说明元素不在显示区域，需要滚动对应的div后重新尝试
            scrollTop=scrollTop+scrollby
            self.jScroll(scrollTop)
            sleep(1)
            switch.click()
            i=i+1
        print('scroll time:%i' % i)
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    @classmethod    
    def jScroll(self, top):
        jscode="$('div.left>div.autoOverflow').scrollTop(%s)" % top
        self.handle.driver.execute_script(jscode)
        
    #从头展开某个部门路径，格式例如'总部/办公厅'，前面的会展开分支，最后一个是点击部门，用于显示部门内容
    @classmethod    
    def expandZtree(self, treeLinks):
        chains=treeLinks.split('/')
        for i in range(0,len(chains)):
            if (i==len(chains)-1):
                #链条的最后一个是点击叶子节点，用于显示部门内容
                print('leaf:%s' % chains[i])
                self.clickLeaf(chains[i])
            else:
                #链条的前面几个会展开分支
                print('branch:%s' % chains[i])
                success = self.toggleBranch(chains[i],'open')
                if (not success):
                    break
            sleep(3)
    '''    
    # 选择流程分支（文本匹配）
    @classmethod
    def selectTransition(self,transitionText):
        if (transitionText=="" or transitionText.lower()=='default'):  #为空或缺省值，则不处理
            return
        
        trans = transitionText.decode(__default_encoding__)
        els = self.handle.elements('','流程分支选择')
        found = False
        for l in els:
            if(trans in l.text):
                c = l.get_attribute('class')
                if (not 'active' in c ):
                    l.click()
                found = True
                break
        #如果找不到，说明流程有变动
        if (not found):
            raise Exception('指定分支（%s）不存在，请检查' % transitionText)
        else:
            sleep(1)
    # 检查页面特定标识，判断当前环节类型，并在对象中设置该标识，以便以合适的方式继续流程
    @classmethod
    def initlize(self,nameList):
        pass

class View():
    # 构造方法，用来接收selenium调用所需的对象
    
    def __init__(self, handle, viewName="",checkSelector="table[id='todo']"):
        self.handle = handle
        self.viewname = viewName
        self.tabs,self.activeTabIndex = self.__getTabs__()
        self.checkSelector = checkSelector
        
    #触发视图是否ready的检查，使用初始化时传入的参数readyFunc
    
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
                    btn = l.find_element_by_tag_name('a').click()
                    sleep(1)
                    found = True
                else:
                    print('the action(%s) had already been disbled, so ignore it' % label.decode(__default_encoding__))
            i=i+1
        if not found:
            print('the action(%s) does no exist, so ignore it' % label.decode(__default_encoding__))
        return found
    #从页面获取所有视图页签名称，返回数组
    
    def __getTabs__(self):
        #获取当前视图页面中的页签，返回对象列表
        tabs = []
        els = self.handle.elements('', '公文页签','')
        i=0
        active=-1
        for l in els:
            label = l.text
            if (label!=''):
                c = l.get_attribute('class')
                if (active==-1 and 'active' in c ):
                    active=i
                tabs.append(label)
                i=i+1
        return tabs,active
    #从对象获取所有视图页签名称，返回数组
    
    def switchToViewTab(self,tabName):
        name=tabName.decode(__default_encoding__)
        els = self.handle.elements('', '公文页签','')
        i=0
        for l in els:
            label = l.text
            c = l.get_attribute('class')
            if (name in label and not 'active' in c ):
                self.activeTabIndex=i
                l.click()
                break
            i=i+1
        sleep(5)
    
    def isTabActivated(self,tabName):
        name=tabName.decode(__default_encoding__)
        tabs=self.tabs
        flag=False
        i=0
        for l in tabs:
            if(name in l and i==self.activeTabIndex):
                flag=True
                break
        return flag
    #判断文档是否在视图中显示（通过文本匹配）
    
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
    
    def clickDocInView(self,docTitle,max_try=10):
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
def toUnicode(str):
    try:
        return str.decode(__default_encoding__)
    except:
        return str
        
class Menu():
    # 构造方法，用来接收selenium调用所需的对象
    @classmethod
    def __init__(self, handle):
        self.handle = handle
    #点击菜单项
    @classmethod    
    def click(self, menus):
        if (menus==""):  #为空，则不处理
            return
        chains=menus.split('/')
        menu1=None
        print(menus.decode(__default_encoding__))
        #根菜单
        els = self.handle.elements("","公文管理根菜单","")
        for l in els:
            #print(l.text)
            if(toUnicode(chains[0]) in l.text):
                actions = AC(self.handle.driver)
                actions.move_to_element(l)
                actions.perform()
                menu1=l
                break
        sleep(1)
        #二级菜单
        if (self.handle.driverType=='ie'):
            #在ie下出现在上级菜单元素下find_element_by_link_text(chains[1].decode('gbk'))找不到元素（ Unable to find element with link text）但firefox下正常，直接在driver下查也正常，怀疑是ie driver的bug，因此先用本函数绕过，以后有时间再查原因吧
            sub=ie_find_element_by_link_text(menu1,chains[1])
            link = sub.get_attribute('href')
            #print('link:%s' % link)
            self.handle.driver.execute_script('window.open("'+link+'")')
        else:
            sub=menu1.find_element_by_link_text(toUnicode(chains[1]))
            if(sub!=None):
                sub.click()
        sleep(3)
#在ie下出现在上级菜单元素下find_element_by_link_text(chains[1].decode('gbk'))找不到元素（ Unable to find element with link text）但firefox下正常，直接在driver下查也正常，怀疑是ie driver的bug，因此用本函数绕过
def ie_find_element_by_link_text(parent,text):
    els=parent.find_elements_by_tag_name('a')
    label = text.decode(__default_encoding__)
    for l in els:
        if(label in l.get_attribute('innerText')):
            print('found element:%s' % l.get_attribute('innerText'))
            return l
    return None
#在视图等场景下，firefox正常，但是ie下，a link可以点击执行，界面上也出现数据加载中提示，但相应的文档窗口没有打开
def ie_click(handle,node):
    #print(node.get_attribute('outerHTML'))
    link = node.get_attribute('href')
    jscript = node.get_attribute('onclick')
    target = node.get_attribute('targrt')
    if(jscript!=''):
        #print('1')
        #处理转义字符，不然移动的sso会出现问题
        jscript = jscript.replace('&amp;','&')
        #print('jscript:%s' % jscript)
        handle.driver.execute_script(jscript)
    elif (link!=''):
        #print('2')
        if(target.lower()=='_blank'):
            #处理转义字符，不然移动的sso会出现问题
            href = href.replace('&amp;','&')
            #print('href:%s' % href)
            href = href.replace('&amp;','&')
            handle.driver.execute_script('window.open("'+href+'")')
        else:
            node.click()
    else:
        print('ie_click cannot handle the link: %s' % node.get_attribute('outerHTML'))
#流程对象
class Workflow():
    # 构造方法
    @classmethod
    def __init__(self, handle, flowName, docTitle='', sourceType='ini'):
        self.handle = handle
        self.config = SmartFlow(flowName,sourceType)
        self.flowName = flowName
        self.title = self.config.getFlowTitle(flowName)
        self.runPaths = self.config.getRunPaths(flowName)
        self.docTitle = docTitle  #保存当前标题，流程中唯一
    def setDocTitle(self,docTitle):
        self.docTitle = docTitle
    # 获取表单填写项
    @classmethod
    def getForm(self,formName):
        return Form(self,formName)

    def getPath(self,name):
        return self.config.getPath(self.flowName,name)
    # 获取节点
    @classmethod
    def getNode(self,nodeName):
        node = WorkflowNode(self,nodeName)
        return node
        
#流程节点对象
class WorkflowNode():
    # 构造方法
    
    def __init__(self, wf,path, nodeName, docTitle=''):
        self.workflow = wf
        self.config = wf.config.getNode(wf.flowName,path,nodeName)
        #print(self.config)
        if(docTitle==''):
            docTitle = wf.docTitle
        self.docTitle = docTitle  #保存当前标题，流程中唯一
        
        if (self.config.has_key('type')):
            self.type = self.config['type']
        else:
            self.type = ''
        
    def setDocTitle(self,docTitle):
        self.docTitle = docTitle
        self.workflow.setDocTitle(docTitle)
    # 获取节点信息
    def get(self,prop,default=''):
        if (self.config.has_key(prop)):
            return self.config[prop]
        else:
            return default
        
    # 获取节点所使用的表单信息
    def getType(self):
        nodeType = self.get('type')
        return nodeType
    # 获取节点所使用的actions
    def getActions(self):
        actions = self.get('actions')
        if actions=='':
            #对应参数不存在
            actions=[]
        else:
            actions=actions.split(';')
        return actions
    def isStop(self):
        actions = self.getActions()
        if('stop' in actions):
            return True
        return False
    def isSkip(self):
        actions = self.getActions()
        if('skip' in actions):
            return True
        return False
    def getGo(self):
        actions = self.getActions()
        ret=-1
        for act in actions:
            if act[0:3].lower()=='go=':
                ret = int(act[3:])
                break
        return ret
    def getForms(self):
        forms = self.getFlows('forms',check=True)
        return forms
    # 获取指定名称的页面流设置，例如flow_setup,forms,flow_teardown
    def getFlows(self,flow_name,default='',check=False):
        if not flow_name:
            flow_name='forms'
        forms =[]
        fnames = self.get(flow_name,default=default)
        
        if (fnames!=''):
            seperators=',;'  #支持的分隔符
            list = re.split('['+seperators+']',fnames)
            for l in list:
                form = self.workflow.getForm(l)
                if form.exists():
                    forms.append(form)
                elif check:
                    #如果强制检查表单有效性，则抛出异常中止
                    raise Exception('Error in getting the setting of form(%s)' % l)
        return forms
    # 根据节点所使用的表单信息，自动填写页面表单
    
    def autoFillForm(self,context={}):
        self.process_node_flow('forms',context=context,skip_empty_field=False,check_form=True)
    def process_node_flow(self,flow_name,context={},default='',skip_empty_field=False,check_form=True):
        #由于之前的node_flow可能会执行全局变量的修改，所以此处需要使用全局变量重新覆盖刷新
        #check_form为True，则加载表单失败后会抛异常，如果为False，则可以跳过（一般用于缺省或内置表单，允许其不存在）
        global_context = self.workflow.handle.system_context
        context = dict(context,**global_context)
        
        
        forms = self.getFlows(flow_name,default=default,check=check_form)
        for f in forms:
            fname = f.name
            self.workflow.handle.logger.debug('====执行页面处理流(%s|%s)=====' % (flow_name,fname))
            prefix = 'dynamicxxxx|'
            if fname.startswith(prefix):
                fname = fname[len(prefix):]
                #动态表格
                self.workflow.handle.logger.debug('====动态表格(%s)=====' % fname)
                dnt = Model_DynamicTable(self.workflow.handle, fname, rootSelector='.dynamicTable',addButton='动态表格添加按钮')
                dnt.add()
                dnt.fields(f.formInputs(),context)
            else:
                #print(f.formInputs())
                self.workflow.handle.fields(f.formInputs(),context,skip_empty_field=skip_empty_field)
            sleep(0.1)
    
    def __str__(self):
        keys=self.config.keys()
        r=''
        for k in keys:
            r = r+'%s:%s, ' %(k,self.config[k])
        return "Flow Node:{%s}" % r
        
#流程节点对象
class Form():
    # 构造方法
    
    def __init__(self, wf, formName):
        self.workflow = wf
        
        self.config = wf.config.getForm(wf.flowName,formName)
        self.name = formName
    # 获取表单信息
    
    def formInputs(self):
        return self.config
    
    def exists(self):
        return len(self.config)>0
    
    def __str__(self):
        r=''
        for i in self.config:
            r = r+'['
            r = r+ ','.join(i)
            r = r+']\n'
        return ("Form:\n[\n%s]" % r)

            
