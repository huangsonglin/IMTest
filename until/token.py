#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/4/12 15:07'

import requests
import time
import hashlib

host = 'http://testapp.dcpai.cn'
url = '/app/interface/mobile/pmall/loginByPhone_220'
headers = {'Content-Type':'application/x-www-form-urlencoded',
            'clientType':'IOS',
            'User-Agent':'Auction/4.5.3 (iPhone; iOS 10.3.3; Scale/2.00)',
            'Accept - Language':"zh-Hans-CN;q=1, en-US;q=0.9",
            'Accept - Encoding':'gzip, deflate',
            'Connection':'keep - alive'}


def get_token(username, password):
    hl = hashlib.md5()
    # 此处必须声明encode
    # 若写法为hl.update(str)  报错为： Unicode-objects must be encoded before hashing
    hl.update(str(password).encode(encoding='utf-8'))
    pw = (hl.hexdigest())
    data = {"phoneNum": username, "pwd": pw}
    lgurl = host + url
    req = requests.post(lgurl, data=data, headers=headers)
    if req.status_code == 200:
        js = (req.json())
        Authorization = js['accessToken']
        return Authorization
    else:
        return req.json()['globalErrors']

