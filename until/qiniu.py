#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/9/9 11:13'

import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import qiniu
from urllib import request
from urllib import response
import random
from until.readTxt import read_file

host = "http://139.196.57.60:9090"
url = '/im/qiniu/getQiniuToken'
headers = {'Content-Type': 'application/x-www-form-urlencoded',
            'clientType': 'IOS',
            'User-Agent': f'Auction/5.0.0 (iPhone; iOS 10.3.3; Scale/2.00)',
            'Connection': 'keep - alive'}
tokenfile = rootPath + r'\TestData\token.txt'

def qiniu_get_token(Authorization):
	qiniuurl = host + url
	headers.update(Authorization=Authorization)
	req = request.Request(qiniuurl, headers=headers)
	print(req.headers, req.full_url)
	RE = request.urlopen(req)
	print(RE.read())

userInfos = random.choice(read_file(tokenfile))
username = userInfos['username']
token = "Bearer % s" %(userInfos['token'])
qiniu_get_token(token)
