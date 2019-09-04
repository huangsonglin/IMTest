#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/9 15:04'



def length(num):
    if isinstance(num, int) or str(num).isdigit():
        return num.to_bytes(4, 'little')
    else:
        raise TypeError('参数类型错误')


