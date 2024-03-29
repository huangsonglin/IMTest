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
        with open(file, encoding='utf-8', errors='ignore') as f:
            # 文件去重处理
            origindata = f.readlines()
            origindata = list(set(origindata))
            for line in origindata:
                if line != '\n':
                    line = line.replace('\n', '')
                    json_data = (eval(line))
                    data.append(json_data)
        return data
    else:
        raise FileExistsError("文件不存在")

