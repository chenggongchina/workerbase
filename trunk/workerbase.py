#encoding=utf8
'''
Created on 2011-9-24

@author: chenggong

worker基类
'''
import time
import os
import re
from optparse import OptionParser
import filelocker

class WorkerBase(object):
    def __init__(self):
        self.patten = ".*"
        self.taskexname = ".txt"
    
    def set_task_patten(self,patten):
        self.patten = patten
    
    def set_task_exname(self,exname):
        self.taskexname = "." + exname.replace(".","")
    
    def dowork(self,filename,content):
        pass
    
    def tasklogic(self,filepath):
        with open(filepath,"r") as filehandle:
            filelocker.lock(filehandle,filelocker.LOCK_NB) #try lock the task
            try:
                self.log("normal",0,"开始执行任务%s"%filepath)
                fsname = os.path.basename(filepath).split(".")[0]
                success = self.dowork(fsname,filehandle.read())
            except Exception,e:
                self.log("warning",0,"派生类未捕获异常%s"%str(e))
            
            filelocker.unlock(filehandle)
            
        while True:
            try:
                if success:
                    self.log("normal",0,"任务%s结束，完成成功"%filepath)
                    finishfile = filepath.split(".")[0]+".finish"
                    if os.path.exists(finishfile):
                        self.log("warning",0,"该任务.finish文件已存在,进行覆盖")
                        os.remove(finishfile)
                    os.rename(filepath,finishfile)
                else:
                    self.log("normal",0,"任务%s结束，完成失败"%filepath)
                    errorfile = filepath.split(".")[0]+".error"
                    if os.path.exists(errorfile):
                        self.log("warning",0,"该任务.erorr文件已存在,进行覆盖")
                        os.remove(errorfile)
                    os.rename(filepath,errorfile)
                break
            except Exception,e:
                self.log("error",0,"任务执行完毕后改名失败,文件系统异常或任务文件已被损坏!except=%s"%str(e))
                time.sleep(5)
    
    def start(self):  
        #params
        taskDir = self.options.dir
        uuid = self.options.uuid
        ip = self.options.ip
        #main loop
        while True:
            try:
                for f in os.listdir(taskDir):
                    filepath = os.path.join(taskDir,f)
                    
                    taskname =  os.path.basename(filepath).split(".")[0]
                    
                    try:
                        if(not re.match(self.patten,taskname)):
                            continue
                    except:
                        self.log("fetal",0,"patten=%s,正则表达式格式匹配失败"%self.patten)
                        return
                    
                    fex = os.path.splitext(f)[1]
                    if fex == "."+uuid: #my task
                        self.log("normal",0,"找到未完成任务%s"%str(f))
                        try:
                            self.tasklogic(filepath)
                        except:
                            self.log("warning",0,"尝试锁定该任务失败,该任务可能已被锁定，uuid=%s可能被多次启用!"%uuid)
                            continue
                    elif fex == self.taskexname: #new task
                        try:
                            os.rename(filepath,"%s.%s.%s"%(filepath,ip,uuid))
                            self.tasklogic("%s.%s.%s"%(filepath,ip,uuid))
                        except:
                            self.log("warning",0,"任务文件%s锁定失败,或已被占有"%filepath)
                            continue
            except:
                self.log("error",0,"连接任务文件夹%s失败，可能网络已断开.."%taskDir)
                time.sleep(30)
        
    def log(self,level,typeid,msg):   
        logdir = self.options.log
        if(not os.path.exists(logdir)):
            os.mkdir(logdir)
        filename = time.strftime('%Y-%m-%d',time.localtime(time.time()))+".log"
        t = time.strftime('%H:%M:%S',time.localtime(time.time()))
        filepath = os.path.join(logdir,filename)

        with open(filepath,"a") as f:
            filelocker.lock(f,filelocker.LOCK_EX) #block lock
            logmsg = "[%8s][%s][%s][%d]%s"%(t,self.options.uuid,level,typeid,msg)
            f.write(logmsg+"\n")
            filelocker.unlock(f)
        print logmsg.decode("utf8").encode("gbk")
    
    def set_options(self,options):
        parser = OptionParser()
        for opt in options:
            parser.add_option(opt['option'], dest=opt['value'])
        ##公用
        parser.add_option("-d", dest="dir")
        parser.add_option("-i", dest="ip")
        parser.add_option("-u", dest="uuid")
        parser.add_option("-l", dest="log")
        (self.options, argvs) = parser.parse_args()
    