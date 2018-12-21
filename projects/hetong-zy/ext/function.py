#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 13:22
# ext/function.py
# 业务功能脚本（用例脚本可调用此处的功能脚本）
import unicodedata



#from encapsulation.mobile_uat import SmartHandle,View
from config.config_01 import browser_config
from encapsulation.webdriver.myerrorhandler import MyErrorHandler

from time import sleep
import time
import re
from log.log import Logger

from selenium.webdriver.common.action_chains import ActionChains as AC
from config import currentProject

SmartHandle=currentProject.innerload('ext.models.SmartHandle')
View=currentProject.innerload('ext.models.View')
Workflow=currentProject.innerload('ext.models.Workflow')
WorkflowNode=currentProject.innerload('ext.models.WorkflowNode')
Form=currentProject.innerload('ext.models.Form')
#全局变量，用于在不同的节点间传送上下文，是的context成为全局的。因为保存context的uihandle可能会被重置，所以，需要在关闭uihandle的同时保存相关context到该全局变量，以后再改进吧:)
__p_sys_context={}

def oa_init(uihandle=None):
    node = None
    #检查uihandle，如果已经存在连接，则关闭之前的连接，并打开新的连接
    if (uihandle!=None and uihandle!=''):
        #之前存在浏览器连接
        #需要先退出之前的浏览器连接
        
        try:
            node = uihandle.cur_node
            driver=uihandle.driver
            if driver:
                driver.quit()
        except:
            pass
    
    driver = init_driver()
    uihandle.init(driver)
    
    uihandle.cur_node=node
    uihandle.system_context = __p_sys_context
    uihandle.windows=[]
    return uihandle
def oa_quit(uihandle):
    #全局变量，用于在不同的节点间传送上下文，使得context成为全局的。因为保存context的uihandle可能会被重置，所以，需要在关闭uihandle的同时保存相关context到该全局变量，以后再改进吧:)
    
    globals()['__p_sys_context'] = uihandle.system_context
    
    #uihandle.closeWindow()
    #添加延时，否则在食药监会报错，估计是窗体正在刷新时关闭引起的
    sleep(1)
    
    uihandle.quit()
def init_driver():
    
    # 打开浏览器
    #driver = browser_config['ie']()
    driver = browser_config['chrome']()
    #driver = browser_config['firefox']()
    #定制异常处理程序
    
    driver.error_handler = MyErrorHandler(driver,screen_shot=True,site='mobile_uat')
    
    #最大化，以避免一些不同初始分辨率引起的错误
    driver.maximize_window() 
    return driver
    
def oa_login(uihandle,username,simple=False):
    #simple参数代表仅登录，不进行后续的登录后表单处理，用于批量注册用户等简单非流程操作
    #打开站点，默认“首页”
    siteName = currentProject.site
    uihandle.openSite(siteName)
    
    sleep(1)

    try:
        user = uihandle.getUser(username)
        id = user[0]
        pwd = user[1]
    except Exception as e:
        raise Exception('Error while getting the Setting of the user(%s)' % username)
    print('user:%s  pwd:%s' % (id,pwd.encode('utf-8')))

    # 调用二次封装后的方法，此处可见操作了哪个页面，哪个元素，msg是要插入的值，插入值的操作在另外一个用例文件中传入
    #uihandel.openPage("登陆页")
    uihandle.Input('登陆页密码输入框', pwd)
    uihandle.Input('登陆页用户名输入框', id)
    uihandle.Click('登陆页登录按钮')
    
    sleep(1)
    if not simple:
        #使用流程excel定义中的登陆后处理表单流
        context = uihandle.system_context
        #执行自定义表单输入流
        if user in ['admin']:
            f_name = 'default_login_管理用户'
        else:
            f_name = 'default_login_普通用户'
        '''
        f = uihandle.cur_node.workflow.getForm(f_name) 
        uihandle.fields(f.formInputs(),context)
        '''
        
        uihandle.fillForm(f_name,context=context)
    
        #关闭注册提示
        #uihandle.Click('注册提示关闭按钮')
        
        sleep(1)
def oa_try(test,uihandle,docTitle="",runPaths='',resume=0,stop=10000,flow='移动学院团委发文',retry=0):
    
    wf = Workflow(uihandle,flow,sourceType='excel')
    wf.setDocTitle(docTitle)
    #从流程配置中获取需要运行检验的路径
    if runPaths=='':
        paths = wf.runPaths
    else:
        seperators=',;'  #支持的分隔符
        paths = re.split('['+seperators+']',runPaths)
    
    #uihandle.logger.info('docTitle:%s' % docTitle)
    
    for p in paths:
        #runPaths为空，说明运行所有流程路径,否则，只允许指定的流程路径
        
        if p in wf.runPaths:
            #该路径需要执行
            
            uihandle=oa_init(uihandle)
            path = wf.getPath(p)
            uihandle.logger.info('\n============开始执行流程（%s）的路径（%s）============' % (flow,p) )
            
            #断点继续,跳过resume之前的节点
            i = resume
            while i<len(path):
                
                uihandle.logger.info('\n===========No.%i node(%s) begin!===========' % (i,path[i]))
                print('\n--No.%i node(%s) begin:' % (i,path[i].decode(__default_encoding__)))
                
                if i>=stop:
                    #运行到指定节点结束，以便人工排查问题
                    break
                #检查路径中的节点，开始一个新流程
                node = WorkflowNode(wf,p,path[i])
                uihandle.cur_node = node
                
                #如果action中有skip，则跳过本节点
                if node.isStop():
                    print('========stopped at node %i' % i)
                    break
                
                #如果action中有skip，则跳过本节点
                if node.isSkip():
                    go = node.getGo()
                    if go>=0:
                        i=go
                    else:
                        i=i+1
                    continue
                    
                attempts = retry
                
                while attempts>=0:
                    if(node.type=='start'):
                        #首节点，意味着流程启动节点
                                oa_test_step_start(test,node)
                    elif node.type=='screenshot':
                        #流程跟踪截图
                        oa_save_flow_track(test,node)
                    elif node.type=='end':
                        #流程结束节点
                        oa_test_step_end(test,node)
                        pass
                    elif node.type=='flow':
                        #流程中间节点
                        oa_test_step_next(test,node)
                        pass
                    elif node.type=='config':
                        #基础配置节点
                        oa_test_config(test,node)
                        pass
                    else:
                        #其他，都用单用户操作环节
                        #oa_test_step_next(test,node)
                        single_step(test,node)
                        #pass
                    #成功执行，则终止尝试循环
                    attempts = -1
                #print(node)
                
                #成功执行后，判断是否需要跳转到指定节点
                go = node.getGo()
                if go>=0:
                    i=go
                else:
                    i=i+1
            #当前路径执行完毕,需要清理环境变量和uihandle,以便开始新的路径执行
            #uihandle = oa_init()
            #wf.handle=uihandle
            globals()['__p_sys_context'] = {}
            

def oa_try2(test,uihandle,docTitle="",runPaths='',resume=0,stop=10000,flow='移动学院团委发文',retry=0):
    
    wf = Workflow(uihandle,flow,sourceType='excel')
    wf.setDocTitle(docTitle)
    #从流程配置中获取需要运行检验的路径
    paths = wf.runPaths
    
    uihandle.logger.info('docTitle:%s' % docTitle)
    
    for p in paths:
        #runPaths为空，说明运行所有流程路径,否则，只允许指定的流程路径
        
        if runPaths=='' or p in runPaths:
            #该路径需要执行
            
            path = wf.getPath(p)
            uihandle.logger.info('\n============开始执行流程（%s）的路径（%s）============' % (flow,p) )
            
            #断点继续,跳过resume之前的节点
            i = resume
            while i<len(path):
                
                uihandle.logger.info('\n===========No.%i node(%s) begin!===========' % (i,path[i]))
                print('\n--No.%i node(%s) begin:' % (i,path[i].decode(__default_encoding__)))
                
                if i>=stop:
                    #运行到指定节点结束，以便人工排查问题
                    break
                #检查路径中的节点，开始一个新流程
                node = WorkflowNode(wf,path[i])
                uihandle.cur_node = node
                
                #如果action中有skip，则跳过本节点
                if node.isStop():
                    print('========stopped at node %i' % i)
                    break

                #如果action中有skip，则跳过本节点
                if node.isSkip():
                    go = node.getGo()
                    if go>=0:
                        i=go-1
                    else:
                        i=i+1
                    continue
                    
                attempts = retry
                
                while attempts>=0:
                    try:
                        if(node.type=='start'):
                            #首节点，意味着流程启动节点
                                    oa_test_step_start(test,node)
                        elif node.type=='screenshot':
                            #流程跟踪截图
                            oa_save_flow_track(test,node)
                        elif node.type=='end':
                            #流程结束节点
                            oa_test_step_end(test,node)
                            pass
                        elif node.type=='flow':
                            #流程中间节点
                            oa_test_step_next(test,node)
                            pass
                        elif node.type=='config':
                            #基础配置节点
                            oa_test_config(test,node)
                            pass
                        else:
                            #其他，都用单用户操作环节
                            #oa_test_step_next(test,node)
                            single_step(test,node)
                            #pass
                        #成功执行，则终止尝试循环
                        attempts = -1
                    except Exception as e:
                        attempts = attempts-1
                        if(attempts<0):
                            #todo 1、重新抛异常。2、在result中记录
                            raise e
                        else:
                            sleep(1)
                            print('step %i failed, try the %i time' % (i,retry-attempts))
                            #uihandle.quit()
                            sleep(4)
                #print(node)
                
                #成功执行后，判断是否需要跳转到指定节点
                go = node.getGo()
                if go>=0:
                    i=go
                else:
                    i=i+1
            #当前路径执行完毕,需要清理环境变量和uihandle,以便开始新的路径执行
            #uihandle = oa_init()
            #wf.handle=uihandle
            globals()['__p_sys_context'] = {}

#设置环境变量
def oa_test_config(test,node):
    uihandle = node.workflow.handle
    if uihandle==None or uihandle=='':
        uihandle = oa_init()
        node.workflow.handle=uihandle
    if uihandle.currentSite=='':
        siteName = currentProject.site
        uihandle.currentSite=siteName
        uihandle.currentPage=''
    
    context = node.workflow.handle.system_context

    user = node.get('user')
    
    
    node.autoFillForm(context)
    
    oa_quit(uihandle)

    #日志
    uihandle.logger.debug('用户操作环节结束'.decode(__default_encoding__))

#进入发文视图，检查指定文档
def single_step(test,node):
    uihandle = oa_init(node.workflow.handle)
    node.workflow.handle=uihandle
    
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    #uihandle = node.workflow.handle
    #docTitle已经作为流程变量参数化，以后应该不需要在程序中定义docTitle了
    #docTitle = node.docTitle
    
    context = node.workflow.handle.system_context

    user = node.get('user')
    
    oa_login(uihandle,user)
    
    sleep(1)
    node.autoFillForm(context)
    
    sleep(1)
    
    oa_quit(uihandle)
    
    #日志
    uihandle.logger.debug('用户操作环节结束'.decode(__default_encoding__))

def oa_test_step_start(test,node):
    uihandle = oa_init(node.workflow.handle)
    node.workflow.handle=uihandle
    #由于需要循环测试，因此必须从登录开始，保证测试的原子性和可重复性
    
    uihandle = node.workflow.handle
    
    #docTitle已经作为流程变量参数化，以后应该不需要在程序中定义docTitle了
    #docTitle = node.docTitle
    
    #context = node.workflow.handle.system_context
    
    transition = node.get('transition')
    #选择分支
    #本oa，利用不同的按钮来实现分支选择
    if transition.lower()=='default':
        transition=''

    
    opinion = node.get('opinion')
    #填写意见，注：由于决策性意见会触发分支的刷新，因此必须先填意见，后选分支
    opinion = opinion[1:]

    user = node.get('user')
    
    assignee = node.get('assignee')
    if assignee.lower()=='default':
        assignee=''
    
    menu = node.get('startMenu')
    
    
    #设置环节内变量
    node_context = {'transition':transition,'opinion':opinion,'user':user,'assignee':assignee,'menu':menu}
    
    
    actions = node.getActions()
    #print("startnode actions:%s" % actions)
    
    oa_login(uihandle,user)
    #uihandle.fillForm('default_start_config',context=node_context,skip_empty_form=True)
    #uihandle.fillForm('default_start_setup',context=node_context,skip_empty_form=True)
    
    node.process_node_flow('flow_setup',context=node_context,default='default_start_setup',skip_empty_field=True,check_form=False)
    
    #context = {'docTitle':docTitle}
    sleep(1)
    node.autoFillForm(context=node_context)
    
    #uihandle.field('','','editor2',context={})
    #处理是否有额外操作，如果有，应在提交前完成
    actions = node.getActions()
    
    #确认提示
    #uihandle.Click("人员提交确定按钮")
    
    #因为需要使用空白值来控制是否执行相应操作，所以必须加上skip_empty_field=True参数
    #uihandle.fillForm('default_start_teardown',context=node_context,skip_empty_field=True,skip_empty_form=True)
    #流程环节结束操作
    node.process_node_flow('flow_teardown',context=node_context,default='default_start_teardown',skip_empty_field=True,check_form=False)
    
    #后续操作，一般用于检查结果
    node.process_node_flow('flow_check',context=node_context,default='default_start_check',skip_empty_field=True,check_form=False)
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    oa_quit(uihandle)
#进入发文视图，检查指定文档
def oa_test_step_next(test,node):
    uihandle = oa_init(node.workflow.handle)
    node.workflow.handle=uihandle
    
    #由于需要循环测试，因此缺省从视图开始，保证测试的原子性和可重复性
    
    transition = node.get('transition')
    #选择分支
    #本oa，利用不同的按钮来实现分支选择
    if transition.lower()=='default':
        transition=''

    
    opinion = node.get('opinion')
    #填写意见，注：由于决策性意见会触发分支的刷新，因此必须先填意见，后选分支
    opinion = opinion[1:]

    user = node.get('user')
    
    assignee = node.get('assignee')
    if assignee.lower()=='default':
        assignee=''
    
    menu = node.get('startMenu')
    
    
    #设置环节内变量
    node_context = {'transition':transition,'opinion':opinion,'user':user,'assignee':assignee,'menu':menu}

    
    actions = node.getActions()
    #print("startnode actions:%s" % actions)
    
    oa_login(uihandle,user)
    #uihandle.fillForm('default_next_config',context=node_context,skip_empty_field=True,skip_empty_form=True)
    #uihandle.fillForm('default_next_setup',context=node_context,skip_empty_field=True,skip_empty_form=True)
    
    node.process_node_flow('flow_setup',context=node_context,default='default_next_setup',skip_empty_field=True,check_form=False)

    #----------------------------------------------------------------------
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    #uihandle = node.workflow.handle

    #docTitle已经作为流程变量参数化，以后应该不需要在程序中定义docTitle了
    #docTitle = node.docTitle
    
    #context = node.workflow.handle.system_context
    
    sleep(0.5)
    node.autoFillForm(context=node_context)
    
    sleep(0.5)
    node.process_node_flow('flow_teardown',context=node_context,default='default_next_teardown',skip_empty_field=True,check_form=False)
    
    #后续操作，一般用于检查结果
    node.process_node_flow('flow_check',context=node_context,default='default_next_check',skip_empty_field=True,check_form=False)
    
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    oa_quit(uihandle)

    #日志
    uihandle.logger.debug('流程中间环节结束'.decode(__default_encoding__))
    
#进入保存流程跟踪的结果
def oa_save_flow_track(test,node):
    uihandle = oa_init(node.workflow.handle)
    node.workflow.handle=uihandle
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    uihandle = node.workflow.handle

    #docTitle已经作为流程变量参数化，以后应该不需要在程序中定义docTitle了
    #docTitle = node.docTitle
    
    context = node.workflow.handle.system_context

    filename = node.get('filename')
    
    user = node.get('user')
   
    oa_login(uihandle,user)
    
    #切换到消息frame
    utsframe = uihandle.element('','消息帧')
    uihandle.driver.switch_to_frame(utsframe)

    view = View(uihandle,'待办视图')
    #todo 未正确加载怎么处理

    #test.assertTrue(view.isDocInView(docTitle))
    #实际出现过早点击，打不开文档
    sleep(20)
    view.clickDocInView(docTitle)
    
    sleep(8)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    
    sleep(3)
   
    #截图验证
    uihandle.Click('流程跟踪按钮')
    sleep(3)
    uihandle.switchWindow('')
    uihandle.save_screenshot('./screenshot/'+docTitle+'_'+filename+'.png')
    
    #todo 解决停止响应问题
    #uihandle.Click('流程跟踪关闭按钮')
 
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    oa_quit(uihandle)



    
#最后一个环节，需要额外处理提示窗
def oa_test_step_end(test,node):
    uihandle = oa_init(node.workflow.handle)
    node.workflow.handle=uihandle
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    uihandle = node.workflow.handle

    #docTitle已经作为流程变量参数化，以后应该不需要在程序中定义docTitle了
    #docTitle = node.docTitle
    
    context = node.workflow.handle.system_context

    transition = node.get('transition')
    opinion = node.get('opinion')
    actions = node.getActions()
    #print(actions)
    
    user = node.get('user')
    #assignee = node.get('assignee')
    
    oa_login(uihandle,user)
    #切换到消息frame
    utsframe = uihandle.element('','消息帧')
    uihandle.driver.switch_to_frame(utsframe)

    view = View(uihandle,'待办视图')


    #截图验证
    #uihandle.save_screenshot('./screenshot/显示公文菜单.png')

    view = View(uihandle,'待办视图')

    #实际出现过早点击，打不开文档
    sleep(15)
    view.clickDocInView(docTitle)
    
    sleep(8)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    sleep(5)
    
    for i in actions:
        if (i=='编号'):
            if uihandle.isDisplayed('编号按钮'):
                uihandle.Click('编号按钮')
                #需要等待时间
                sleep(3)
                try:
                    #已经编过号，这里弹出确认提示，需要关闭
                    alt = uihandle.driver.switch_to_alert()
                    print('alert prompt: %s' % alt.text)
                    alt.accept()
                    sleep(3)
                except:
                    #没编过号
                    pass
                uihandle.Click('编号确定按钮')
                sleep(3)
        elif (i.startswith("表单截图|")):
            #截图字串样例 '表单截图|align=top&selector=#mainToId_th&prefix=意见截图'
            uihandle.formScreenShot(i)
        elif (i=="发送文件"):
            #只为了兼容以前的用例，因为参数都写死在代码里了，所以最终应该会废弃掉
            #发送文件
            uihandle.field('发送文件按钮','multi|部门:财务部,技术部;分公司:北京,河北','fenfa_org')
            sleep(5)
        elif (i.startswith("发送文件|")):
            #发送文件
            i=i.replace('发送文件','multi').replace('&',',')
            #i最终格式'multi|部门:财务部,技术部;分公司:北京,河北'
            uihandle.field('发送文件按钮',i,'fenfa_org')
            sleep(10)
        elif (i=='发送文件_只确认'):
            uihandle.logger.info("发送文件:直发，无参数".decode(__default_encoding__))
            #处理直接发送文件，不需要选择，只确认的情况
            uihandle.Click('发送文件按钮')
            sleep(5)
            alt = uihandle.driver.switch_to_alert()
            if(alt.text!=''):
                uihandle.logger.debug("执行发送文件操作:返回确认提示（“%s”）".decode(__default_encoding__) % alt.text)
                alt.accept()
                
                sleep(4)
                
                #发送成功确认
                alt = uihandle.driver.switch_to_alert()
                if(alt.text!=''):
                    uihandle.logger.debug("执行发送文件操作:返回成功提示（“%s”）".decode(__default_encoding__) % alt.text)
                    alt.accept()
            #需要等待页面刷新，不然后续页面还没刷出来就执行了，会报错
            sleep(10)
        elif (i=='归档'):
            print('检查是否已经归档'.decode(__default_encoding__))
            if uihandle.isDisplayed('归档按钮'):
                print('执行归档'.decode(__default_encoding__))
                uihandle.Click('归档按钮')
                #需要等待时间
                sleep(3)
                
                #确认归档提示
                alt = uihandle.driver.switch_to_alert()
                print('alert prompt: %s' % alt.text)
                alt.accept()
                sleep(3)
                #没有alert，说明还没有归档过
                if uihandle.isDisplayed('归档确定按钮'):
                    uihandle.setArchive("短期")
                    uihandle.Click('归档确定按钮')
                    sleep(2)
                
                #归档成功确认
                alt = uihandle.driver.switch_to_alert()
                print('alert prompt: %s' % alt.text)
                alt.accept()
                #等待归档带来的页面刷新
                sleep(15)
            else:
                print('已归档，不再另行归档'.decode(__default_encoding__))
   
    uihandle.Click('提交下一处理')
    #todo检查是否成功提交
    sleep(2)
    
    #填写意见，注：由于决策性意见会触发分支的刷新，因此必须先填意见，后选分支
    if (opinion!=''):
        uihandle.setOpinion(opinion)
            
    #选择分支
    if transition.lower()=='default':
        transition=''
    if (transition!=''):
        uihandle.selectTransition(transition)
    print('-opinion:%s \n-transition:%s' % (opinion.decode(__default_encoding__),transition.decode(__default_encoding__)))
    #提交前面的意见和流程分支窗体
    if (opinion!='' or transition!=''):
        sleep(0.5)
        uihandle.submitOpinion()
    
    #处理多个确认
    i=0
    while i<3:
        try:
            alt = uihandle.driver.switch_to_alert()
            print('alert prompt: %s' % alt.text)
            alt.accept()
            sleep(1)
            print('alert end')
            i=i+1
        except:
            break
        
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    oa_quit(uihandle)