#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/9 13:51'

import socket
import os, sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)



sever = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_prot = ("139.196.57.60", 9999)
# 监听服务器
sever.bind(ip_prot)
sever.listen(5)
conn, addr = sever.accept()
#关闭连接
conn.close()
sever.close()
