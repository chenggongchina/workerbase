#encoding=utf8
'''
Created on 2011-9-24

@author: chenggong

worker例程
'''


from workerbase import WorkerBase
import time

#派生WorkBase
class SampleWorker(WorkerBase):
    
    #实现dowork方法
    # filepath  :任务文件名，
    # filehandle:任务文件内容
    def dowork(self,filepath,content):
        print "dowork file=%s content=%s"%(filepath,content)
        print "doing..."
        
        #由self.options.xxxx可以获取自己设置的参数
        print "myparam=%s %s"%(self.options.test1,self.options.test2) 

        time.sleep(2)
        
        #日志提交方法
        self.log("debug",0,"可以这样提交日志") 
        
        #成功则返回True，失败返回False
        return False 

'''
基本命令行参数，调用至少要有以下几个参数
-d 任务文件夹
-l 日志输出文件夹
-i 本机IP
-u uuid
'''

if __name__ == "__main__":
    #实例化SampleWorker
    sampleworker = SampleWorker()
    
    #设置自己的任务文件匹配方式，若不设置，则默认为全匹配
    #如下，则匹配  xxx-xxx-cut 所有文件
    sampleworker.set_task_patten(".*-.*-cut")
    
    #设置任务文件扩展名，若不设置，则默认为txt
    sampleworker.set_task_exname("txt")

    #设置自己的参数
    sampleworker.set_options([{"option":"-a","value":"test1"},{"option":"-b","value":"test2"}])
    
    #开始主循环
    sampleworker.start()