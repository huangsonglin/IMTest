#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/19 17:18'


import os
import sys
import json
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


def read_file(file):
    data = []
    if os.path.exists(file):
        with open(file, encoding='utf-8') as f:
            for line in f.readlines():
                if line != '\n':
                    line = line.replace('\n', '')
                    json_data = (eval(line))
                    data.append(json_data)
        return data
    else:
        raise FileExistsError("文件不存在")

read_file(r'D:\TestWork\DCIM\TestData\recv_data.txt')