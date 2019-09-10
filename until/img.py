#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/9/9 10:16'

import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from PIL import Image
import image
import random
import json
from urllib import response
from urllib import request
from urllib import parse
from until.mysql import Mysql
from concurrent.futures import ThreadPoolExecutor, wait
import threading

imgpath = rootPath + r'\img\\'
imgUrl = 'http://testimg.dcpai.cn/'

def get_img():
    allfiles = os.listdir(imgpath)
    if len(allfiles) == 0:
        imgs = Mysql().sql_result(f'select images from product order by rand() limit 10')
        imgList = []
        for img in imgs:
            if img[0] != None:
                singList = img[0].split(',')
                for sing in singList:
                    imgList.append(sing)
        for IMG in imgList:
            FullIMG = imgUrl + IMG
            File = request.urlretrieve(FullIMG, imgpath+IMG)
        allfiles = os.listdir(imgpath)
    IMG = random.choice(allfiles)
    im = Image.open(imgpath + IMG)
    result = json.dumps({"width": im.size[0], "url": IMG, "height": im.size[1]})
    return result
