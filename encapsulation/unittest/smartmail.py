#!/usr/bin/python
# -*- coding: utf-8 -*-
import email
import mimetypes
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText
# from email.MIMEImage import MIMEImage
import smtplib
import time

class SmartMail(object):
    '''mail function used by smartdot testing
    '''
    def __init__(self,config={}):
        self.config = config
        
        self.readConfigs()
    def readConfigs(self):
        self.fromaddr = self.getConfig('fromaddr')
        self.toaddr = self.getConfig('toaddr')
        self.server = self.getConfig('server')
        self.username = self.getConfig('username')
        self.password = self.getConfig('password')
        self.subject = self.getConfig('subject')
        self.htmltext = self.getConfig('htmltext')
        self.plaintext = self.getConfig('plaintext')
        self.debuglevel = self.getConfig('debuglevel')
    def getConfig(self, para_name, default_value=''):
        cf = self.config
        if(cf.has_key(para_name)):
            v = cf[para_name]
        else:
            v = default_value

        return v
        
    def send(self,config={}):
        #将新输入的配置项合并，保存
        cf = dict(self.config,**config)
        self.config = cf
        self.readConfigs()
        
        strFrom = self.fromaddr
        
        if type(self.toaddr)==list:
            strTo = ', '.join(self.toaddr)
        else:
            strTo = self.toaddr
        
        server = self.server
        user = self.username
        
        passwd = self.password
        if not (server and user and passwd) :
            print('incomplete login info, exit now')
            return
        # 设定root信息
        
        if not(strTo):
            print('no receipt info, exit now')
            return
        
        msgRoot = MIMEMultipart('related')
        try:
            subject = self.subject.decode('gbk')
        except:
            subject = self.subject
        msgRoot['Subject'] = self.replace_with_key(subject)
        #pdb.set_trace()
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        #设定纯文本信息
        msgText = MIMEText(self.plaintext, 'plain', 'utf-8')
        msgAlternative.attach(msgText)
        #设定HTML信息
        msgText = MIMEText(self.htmltext, 'html', 'utf-8')
        msgAlternative.attach(msgText)
        #设定内置图片信息
        '''
        fp = open('./screenshot/显示公文菜单.png'.decode('gbk')), 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)
        '''
        #发送邮件
        smtp = smtplib.SMTP()
        #设定调试级别，依情况而定
        smtp.set_debuglevel(self.debuglevel)
        smtp.connect(server)
        smtp.login(user, passwd)
        smtp.sendmail(strFrom, strTo, msgRoot.as_string())
        smtp.quit()
        return  
    #检查传入的字串是否是可替换关键字，这里有两种（静态关键字和公式关键字），静态关键字可以直接用context替换，公式关键字类似now[fmt:yyyy-m-d]，需要有业务逻辑计算扩展
    def replace_with_key(self,source):
        f1='$now'
        start_p = source.find('$now')
        if start_p>=0:
            end_p = source.find('$',start_p+len(f1))
            if end_p>0:
                fmtstr=source[start_p+len(f1):end_p]
                f2='[fmt:'
                fmt=''
                start_p2 = fmtstr.find(f2)
                if start_p2>=0:
                    end_p2 = fmtstr.find(']',start_p2+len(f2)+1)
                    if end_p2>0:
                        fmt=fmtstr[start_p2+len(f2):end_p2]
                if fmt=='':
                    fmt='%Y-%m-%d'
                now = time.strftime(fmt, time.localtime(time.time()))   
                
                ret = "%s%s%s" % (source[0:start_p],now,source[end_p+1:])
                return ret
        return source
