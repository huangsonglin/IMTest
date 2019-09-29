#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/29 15:07'

import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import pymongo as pmg
import datetime, time
import re


host = '139.196.57.60'
port = 27017


def mgdb(table, sql, *keyword):
	result = []
	# 请求连接mogo
	mg = pmg.MongoClient(host, port)
	# 使用数据库
	db = mg['im']
	# 获取数据库下表集合
	stbs = db.list_collection_names()
	# 连接某文档/表
	if table in stbs:
		stb = db[table]
		# 执行查询操作
		datas = stb.find(sql).sort(*keyword)
		for data in datas:
			result.append(data)
	else:
		raise ValueError('参数错误')
	return result

def return_mgdb(table):
	# 请求连接mogo
	mg = pmg.MongoClient(host, port)
	# 使用数据库
	db = mg['im']
	# 获取数据库下表集合
	stbs = db.list_collection_names()
	# 连接某文档/表
	stb = db[table]
	return stb

if __name__ == '__main__':
	sql = {"_id": "5258:5273:196"}
	messageList = return_mgdb('userMessage:%s.' % 5258)
	res = messageList.find_one(sql)
	print(res['read'])