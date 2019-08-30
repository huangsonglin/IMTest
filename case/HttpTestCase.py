#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/29 10:35'

import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import unittest
import random
import re
import json
import math
from HttpApi.httpapi import *
from until.readTxt import read_file
from until.mysql import Mysql
from until.mogo import mgdb
from concurrent.futures import ThreadPoolExecutor, wait

class unitest_http_api(unittest.TestCase):

	tokenfile = rootPath + r'\TestData\token.txt'
	clientType = random.choice(['IOS', 'ANDROID'])
	version = '5.0.0'
	result_file = rootPath + r'\TestData\result.txt'
	fp = open(result_file, 'a', encoding='utf-8')


	def setUp(self):
		self.fp.write('=' * 100 + '\n')

	def tearDown(self):
		self.fp.write('=' * 100 + '\n')
		self.fp.close()

	# 查询某用户的聊天列表
	def test_001_Message_Controller_chat(self):
		userInfos = random.choice(read_file(self.tokenfile))
		username = userInfos['username']
		token = "Bearer % s" %(userInfos['token'])
		req = Message_Controller(self.clientType, self.version).chat(token)
		try:
			self.assertEqual(req.status_code, 200, msg="接口请求调用成功")
			datas = Mysql().sql_result\
				(f'SELECT friend_id FROM im_user_friend WHERE user_id='
				 f'(select id from  user where username={username}) ORDER BY id ASC')
			self.assertEqual(len(req.json()), len(datas), msg="查询结果和数据库保持一致")
			rdatas = []
			for result in req.json():
				rdatas.append((int(result['id']) , ))
			self.assertEqual(sorted(datas), sorted(rdatas))
			self.fp.write(f'======查询某用户的聊天列表测试结果：True======\n')
		except:
			self.fp.write(f'======查询某用户的聊天列表测试结果：False======\n')

	# 查询与某人的历史聊天记录(给定时间之前的消息)
	def test_002_User_Controller_backward(self):
		userInfos = random.choice(read_file(self.tokenfile))
		username = userInfos['username']
		token = "Bearer % s" % (userInfos['token'])
		memberId = Mysql().reslut_replace(f'select id from user where username={username}')
		to_userId = str(random.choice(list(range(5152, 5201)) + list(range(5248, 5297))))
		if int(to_userId) > int(memberId):
			rex = f'{memberId}:{to_userId}'
		else:
			rex = f'{to_userId}:{memberId}'
		systime = datetime.datetime.now()
		systime_timestamp = int(systime.timestamp() * 1000)
		sqljson = {"$and":[{"_id":re.compile(rex)}, {"createTime":{"$lte":systime}}]}
		req = User_Controller(self.clientType, self.version).backward(token, to_userId, systime_timestamp)
		mbresult = mgdb('userMessage:%s.' %memberId, sqljson, "createTime", -1)
		try:
			for i in range(len(req.json())):
				self.assertEqual(req.json()[i]['id'], mbresult[i]['_id'], msg='消息记录id保持一致')
				self.assertEqual(u'%s' % req.json()[i]["content"], u'%s' % mbresult[i]['content'])
			self.fp.write(f'======查询与某人的历史聊天记录(给定时间之前的消息)：True======\n')
		except:
			self.fp.write(f'======查询与某人的历史聊天记录(给定时间之前的消息)：False======\n')

	# 查询与某人的历史聊天记录(给定时间之前的消息)
	def test_003_User_Controller_forward(self):
		userInfos = random.choice(read_file(self.tokenfile))
		username = userInfos['username']
		token = "Bearer % s" % (userInfos['token'])
		memberId = Mysql().reslut_replace(f'select id from user where username={username}')
		to_userId = str(random.choice(list(range(5152, 5201)) + list(range(5248, 5297))))
		if int(to_userId) > int(memberId):
			rex = f'{memberId}:{to_userId}'
		else:
			rex = f'{to_userId}:{memberId}'
		aftertime = datetime.datetime.now() - datetime.timedelta(days=2)
		aftertime_timestamp = int(aftertime.timestamp() * 1000)
		sqljson = {"$and":[{"_id":re.compile(rex)}, {"createTime":{"$gte":aftertime}}]}
		req = User_Controller(self.clientType, self.version).forward(token, to_userId, aftertime_timestamp)
		mbresult = mgdb('userMessage:%s.' %memberId, sqljson, "createTime", -1)
		try:
			for i in range(len(req.json())):
				self.assertEqual(req.json()[i]['id'], mbresult[i]['_id'], msg='消息记录id保持一致')
				self.assertEqual(u'%s' % req.json()[i]["content"], u'%s' % mbresult[i]['content'])
			self.fp.write(f'======查询与某人的历史聊天记录(给定时间之后的消息)：True======\n')
		except:
			self.fp.write(f'======查询与某人的历史聊天记录(给定时间之后的消息)：False======\n')
			pass

	# 删除和某个用户的私聊信息
	def test_004_User_Controller_delete_withuser(self):
		userInfos = random.choice(read_file(self.tokenfile))
		username = userInfos['username']
		token = "Bearer % s" % (userInfos['token'])
		memberId = Mysql().reslut_replace(f'select id from user where username={username}')
		to_userId = str(random.choice(list(range(5152, 5201)) + list(range(5248, 5297))))
		req = User_Controller(self.clientType, self.version).delete_withuser(token, to_userId)
		try:
			self.assertEqual(req.status_code, 200, msg="接口正常调通")
			if int(to_userId) > int(memberId):
				rex = f'{memberId}:{to_userId}'
			else:
				rex = f'{to_userId}:{memberId}'
			sql = {{"_id":re.compile(rex)}}
			mgresult = mgdb('userMessage:%s.' %memberId, sql, "createTime", -1)
			self.assertEqual(len(mgresult), 0, msg="删除与他人得私聊信息功能正常")
			self.fp.write(f'======删除和某个用户的私聊信息：True======\n')
		except:
			self.fp.write(f'======删除和某个用户的私聊信息：False======\n')

	# 用户删除某条私聊消息
	def test_005_User_Controller_delete_message(self):
		userInfos = random.choice(read_file(self.tokenfile))
		username = userInfos['username']
		token = "Bearer % s" % (userInfos['token'])
		memberId = Mysql().reslut_replace(f'select id from user where username={username}')
		mgresult = mgdb('userMessage:%s.' %memberId, None, '_id', 1)
		messageIds = []
		for data in mgresult:
			messageIds.append(data['_id'])
		InMessage = random.sample(messageIds, random.randint(1, math.ceil(len(messageIds)/10)))
		newMessageIds = []
		for data in messageIds:
			if data not in InMessage:
				newMessageIds.append(data)
		ErrorMessage = [newMessageIds[0], f'-1:{int(memberId)+1}:1']
		testData = [InMessage, ErrorMessage]
		for data in testData:
			req = User_Controller(self.clientType, self.version).delete_message(token, data)
			if len(data) != 0:
				self.assertEqual(req.status_code, 200)
				for messageid in data:
					sql = {'_id': messageid}
					mgr = mgdb('userMessage:%s.' %memberId, sql, '_id', 1)
					self.assertEqual(len(mgr), 0)





