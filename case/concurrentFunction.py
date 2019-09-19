#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/19 11:17'


import os, sys
import io
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import socket
import random
import numpy as np
import pandas as pd
import time, datetime
import csv
import json
import threading
import multiprocessing
import emoji
import queue
from shutil import copyfile
from temp.message_pb2 import *
from temp.protomsg import *
from until.length import length
from until.chinese import chineseText
from until.readTxt import read_file
from concurrent.futures import ThreadPoolExecutor, wait
from until.img import get_img
from case.test_tcp_case import Function

# 采用线程池方式接收消息
def Function_concurrent_testing(concurrentNum, username):
    pool = ThreadPoolExecutor(max_workers=concurrentNum)
    futures = []
    for i in range(concurrentNum):
        f1 = pool.submit(Function().Recv, username)
        futures.append(f1)
    wait(futures)

# 多线程池方式发送消息
def Function_concurrent_sendmessage(concurrentNum, tousername):
    memberId = Mysql().reslut_replace(f'select id from user where username={tousername}')
    IMG = get_img()
    pool = ThreadPoolExecutor(max_workers=concurrentNum)
    futures = []
    for i in range(concurrentNum):
        TXT = [chineseText(random.randint(1, 100)),
               ''.join(random.sample(list(emoji.unicode_codes.EMOJI_UNICODE.values()), 10)),
               IMG]
        content = random.choice(TXT)
        if str(content).startswith('{') and str(content).endswith('}'):
            try:
                json.loads(content)
                contenType = "IMG"
            except:
                contenType = "TXT"
        else:
            contenType = "TXT"
        fromuser = random.randint(40000000000, 40000000049)
        f1 = pool.submit(Function().Send, fromuser, contenType, content, int(memberId), "IOS")
        futures.append(f1)
    wait(futures)