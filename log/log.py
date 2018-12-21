#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-17 11:19
# log/log.py

import logging
import logging.handlers
import sys,os


_srcfile=__file__.lower().replace('.pyc','.py')
def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        #print(dir(sys.exc_info()[2].tb_frame))
        return sys.exc_info()[2].tb_frame.f_back
def findCaller():
    #由于多包了一层log.py，导致log日志中都记载的是log.py，而不是调用该封装的程序，此处不去修改logging，用变通的方法实现(adapter的extra)
    """
    Find the stack frame of the caller so that we can note the source
    file name, line number and function name.
    """
    f = currentframe()
    #On some versions of IronPython, currentframe() returns None if
    #IronPython isn't run with -X:Frames.
    if f is not None:
        f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)"
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        #print ('file:%s vs %s' % (filename,_srcfile))
        if filename == _srcfile:
            f = f.f_back
            continue
        rv = (co.co_filename, f.f_lineno, co.co_name)
        break
    return rv
class MyLoggerAdapter(logging.LoggerAdapter):
    #由于多包了一层log.py，导致log日志中都记载的是log.py，而不是调用该封装的程序，此处不去修改logging，用变通的方法实现(adapter的extra)

    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs["extra"] = self.extra
        return msg, kwargs

# 日志类
class Logger():
    LOG_ID = 'mylogs'
    LOG_FILE = 'mylogs.log'
    #fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s - %(ip)s'
    fmt = '%(asctime)s - %(myfilename)s:%(mylineno)s - %(myfuncName)s - %(message)s'
    
    handler = None
    logger = None
    formatter = None
    handlers={}

    def __init__(self,log_id='',log_file='',fmt=''):
        if log_id!="":
            self.LOG_ID=log_id
        if log_file!="":
            self.LOG_FILE==log_file
        if fmt!="":
            self.fmt = fmt
        #pdb.set_trace()
        handler = logging.handlers.RotatingFileHandler(self.LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler

        self.formatter = logging.Formatter(self.fmt)   # 实例化formatter
        handler.setFormatter(self.formatter)      # 为handler添加formatter

        __logger = logging.getLogger(self.LOG_ID)    # 获取名为tst的logger
        
        #检查对应的handler是否已经存在，不存在则加入，存在，则覆盖
        handlers = Logger.handlers
        if handlers.has_key(self.LOG_ID):
            #已存在，多半是之前的日志实例所添加，先删除，后添加，相当于覆盖
            hdls = handlers[self.LOG_ID]
            for h in hdls:
                __logger.removeHandler(h)
        handlers[self.LOG_ID]=[handler]
        __logger.addHandler(handler)           # 为logger添加handler
        __logger.setLevel(logging.DEBUG)
        
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        #console_formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console_formatter = logging.Formatter('【%(levelname)s】%(message)s'.decode(__default_encoding__))
        console.setFormatter(console_formatter)
        # 将定义好的console日志handler添加到logger
        handlers[self.LOG_ID].append(console)
        logging.getLogger(self.LOG_ID).addHandler(console)
        
        extra_dict = {}
        self.logger = MyLoggerAdapter(__logger, extra_dict)
    
    def toUnicode(self,v):
        t=type(v)
        if t == str:
            r = v.decode(__default_encoding__)
        elif t== float:
            #特殊处理，因为excel数字域默认是float类型，转换后4会变成4.0,应急处理，以后再想好的办法。
            if(v==int(v)):
                r = "%i" % v
            else:
                r = "%s" % v
        elif  t== unicode:
            r = v
        else:
            print('!!!!!!there is still other type to deal:%s' % type(v))
            r = v
        return r
    
    def loginfo(self, message):
        filename, lineno, co_name = findCaller()
        #print("-file:%s\ncode:%s\nline:%s" % (filename,co_name,lineno))
        self.logger.info(self.toUnicode(message),extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})

    def logdebug(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.debug(self.toUnicode(message),extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})
        
    def info(self, message):
        filename, lineno, co_name = findCaller()
        #print("-file:%s\ncode:%s\nline:%s" % (filename,co_name,lineno))
        self.logger.info(self.toUnicode(message),extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})

    def debug(self, message):
        filename, lineno, co_name = findCaller()
        
        self.logger.debug(self.toUnicode(message),extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})
        
    def warning(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.warning(self.toUnicode(message),extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})
    def error(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.error(self.toUnicode(message),extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})
    def critical(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.critical(self.toUnicode(message),extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})