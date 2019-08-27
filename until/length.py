#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/9 15:04'


def length(str):
    if len(str) < 4:
        str = str.rjust(4, '0')
    return str
