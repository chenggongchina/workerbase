WORKERBASE
==============================

WORKERBASE是一个超小型基于文件系统的任务分发、执行框架，使用python编写
框架不实现map/reduce级别的任务拆分和调度，本文设计的调度框架只满足以下几点特性：


* 轻量级，代码框架及实现原理非常简单，容易部署
* 集群可扩展，理论上集群机器数量，以及每台机器上的执行任务数都可扩展
* 业务单元化，业务定义的下发任务是具体的、可颗粒化的，本框架不辅助做任务或工作流的拆分，只接受最细颗粒化的任务


实现原理：
================================
* 所有计算节点（这里指一个程序实例）均地位平等
* 任务以一个文件的形式存在，计算节点通过共享文件系统去“抢”任务。* 所有的计算节点均永久存在，不断的扫描任务文件* 业务系统下发任务，即直接生成一个文件


	我们将计算节点定义为worker，那么worker的主逻辑如下
<pre><code>
While(true){
         If(find(以前未完成的任务文件)||find(任务文件)){
                   将该文件增加扩展名+本机ip.实例号
                   处理任务
                   将任务文件迁移到finish目录
       }
}
</pre></code>