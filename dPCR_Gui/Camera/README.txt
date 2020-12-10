********************************************************

      Windows 环境 Galaxy python 安装说明
    
                  2019-11-20

********************************************************


Python2.7(3.5) gxipy 安装步骤  
=============================

1.安装 python2.7(3.5)

  (1)从python官网下载用于Windows(x86/x86_64)系统的python2.7(3.5)安装包并执行安装。
    
     下载网址: https://www.python.org/downloads/windows/

  (2) 在系统环境变量中添加python.exe的路径。
 
2.安装 pip 工具

  (1) 打开网址 https://pip.pypa.io/en/stable/installing/ ，下载 get-pip.py.

  (2) 通过CMD打开DOS命令窗口，切换路径到get-pip.py所在目录。

  (3) 在DOS命令窗口中输入以下命令完成pip安装。 
    
      python get-pip.py

  (4) 在系统环境变量中添加pip.exe的路径。

3.安装 numpy 库
 
  在DOS命令窗口中输入以下命令。

      pip install numpy


注意：
=============================

  （1）示例程序可能依赖第三方库（例如 PIL），请自行安装。

  （2）Python示例程序须同gxipy放置于同一目录才可执行。
  
  （3）如果用户开发的程序依赖gxipy库，需要将该目录下gxipy复制到用户开发目录。


