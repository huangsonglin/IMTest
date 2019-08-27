#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/4/12 16:45'

import string
import random


def chineseText(num):
    varchar = ''
    if str(num).isdigit():
        for i in range(int(num)):
            Text = chr(random.randint(0x4e00, 0x4e73))
            varchar += Text
    return varchar