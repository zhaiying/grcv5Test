#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-01-25 13:20
# config/__init__.py


__all__=['ProjectSuit','suit','Project','currentProject']

import unittest
import pdb

from encapsulation.unittest.SmartHTMLTestRunner import SmartHTMLTestRunner
import time,os,datetime

import configparser

class ProjectSuit(object):
    run=[]
    #    currentProject=None
    currentProject='hetong-zy'
    seq=-1
    def __init__(self):
        self.cf_file=os.path.join('projects', 'projects.ini')
        self.readProjects()
        self.currentProject=self.getNext()
    def readProjects(self):
        cf = configparser.ConfigParser()
        cf.read(self.cf_file)
        runs=cf.get('projects','runs')
        project_ids=runs.split(',')
        self.project_ids = project_ids
        
    def getNext(self):
        
        ids=self.project_ids
        if(len(ids)==0):
            return None
        seq = self.seq+1
        if(seq>=len(ids)):
            #the last one
            return None
        project_id = ids[seq]
        if not (project_id):
            return None
        else:
            self.seq=seq
            return Project(project_id)

class Project(object):
    id=''
    path=''
    #mail configuration
    mail_server=''
    mail_user=''
    mail_password=''
    mail_debug_level=0
    mail_from_addr=''
    mail_to_addr=''
    mail_subject=''
    #summary configuration
    summary='report;mail'
    #report configuration
    report_title=''
    report_description=''
    report_path='report'
    report_filename='$now[fmt:%Y-%m-%d_%H_%M_%S]$_result.html'
    #testing configuration
    testcase_path=''
    testcase_pattern='start_*.py '
    
    def __init__(self,project_id):
        self.cf_file=os.path.join('projects',project_id, 'project.ini')
        self.read()
        
    def readFromIni(self,filename):
        pass
    def read(self):
        cf = configparser.ConfigParser()
        cf.read(self.cf_file)
        self.read_project(cf)
        self.read_mail(cf)
        self.read_report(cf)
        self.read_testing(cf)
    def read_project(self,cf):
        #project configuration
        self.id=self.get(cf,'project','id')
        self.path=self.id
        self.root_path=os.path.join('projects',self.path)
        self.site=self.get(cf,'project','site')
    def read_mail(self,cf):
        #mail configuration
        self.mail_server=self.get(cf,'mail','server')
        self.mail_user=self.get(cf,'mail','user')
        self.mail_password=self.get(cf,'mail','password')
        self.mail_debug_level=self.get(cf,'mail','debuglevel',0,value_type=int)
        self.mail_from_addr=self.get(cf,'mail','fromaddr')
        self.mail_to_addr=self.get(cf,'mail','toaddr')
        self.mail_subject=self.get(cf,'mail','subject')
    def read_report(self,cf):
        #report configuration
        self.report_title=self.get(cf,'report','title')
        self.report_description=self.get(cf,'report','description')
        self.report_path=self.get(cf,'report','path','report')
        self.report_filename=self.get(cf,'report','filename','$now[fmt:%Y-%m-%d_%H_%M_%S]$_result.html')
    def read_testing(self,cf):
        #testing configuration
        self.testcase_path=self.get(cf,'testcase','path')
        self.testcase_pattern=self.get(cf,'testcase','pattern')
        
    def get(self,cf,section,key,default_value='',value_type=str, force=False):
        
        try:
            v=cf.get(section,key)
        except:
            if(force):
                raise Exception('can not get the configuration(section=%s,key=%s) from ini(%s)' % (section,key,self.cf_file))
            else:
                v=default_value
        try:
            if value_type!=str and type(v)!=value_type:
                v=value_type(v)
        except:
            raise Exception('can not get proper type of the configuration(section=%s,key=%s) from ini(%s)' % (section,key,self.cf_file))
        return v
    def load(self, name, module=None):
        """
        dynamic loading class,function,variable,and so on
        """
        parts = name.split('.')
        if module is None:
            parts_copy = parts[:]
            while parts_copy:
                try:
                    module = __import__('.'.join(parts_copy))
                    break
                except ImportError:
                    del parts_copy[-1]
                    if not parts_copy:
                        raise
            parts = parts[1:]
        obj = module
        for part in parts:
            try:
                parent, obj = obj, getattr(obj, part)
            except:
                pdb.set_trace()
        return obj
    def innerload(self, name, module=None):
        """
        dynamic loading class,function,variable,and so on
        """
        newname='projects.%s.%s' % (self.id,name)
        return self.load(newname, module)
    # 取test_case文件夹下所有用例文件
    def testsuit(self):
        lists=os.path.join('projects',self.id, self.testcase_path)

        #lists='projects\\%s\\%s' % (self.id,self.testcase_path)
        testunit = unittest.TestSuite()
        # discover 方法定义
        discover = unittest.defaultTestLoader.discover(lists, pattern=self.testcase_pattern, top_level_dir=None)
        #discover 方法筛选出来的用例，循环添加到测试套件中
        for test_suite in discover:
            for test_case in test_suite:
                testunit.addTests(test_case)
                print(testunit)
        return testunit
    def runtests(self):

        alltests = self.testsuit()

        #测试报告文件名中
        filename=self.report_filename
        fmt=''
        if(filename.startswith('$now[fmt:')):
            f='$now[fmt:'
            n=filename.find(']$',len(f)+1)
            if n>0:
                fmt=filename[len(f):n]
        if(fmt!=''):
            now = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(time.time()))
            filename = os.path.join('projects',self.id,self.report_path, '%s_result.html' % now)  #定义报告存放路径和文件名。

        tests=self.testsuit()
        fp = open(filename, 'wb')
        runner = SmartHTMLTestRunner(stream=fp, title=self.report_title, description=self.report_description, project=self)
        runner.run(tests)
        fp.close()

suit=ProjectSuit()   
currentProject = suit.currentProject