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
from until.mogo import mgdb, return_mgdb
from concurrent.futures import ThreadPoolExecutor, wait

class Test_http_api(unittest.TestCase):

	tokenfile = rootPath + r'\TestData\token.txt'
	clientType = random.choice(['IOS', 'ANDROID'])
	version = '5.0.0'
	result_file = rootPath + r'\TestData\result.txt'
	fp = open(result_file, 'a', encoding='utf-8')


	def setUp(self):
		pass

	def tearDown(self):
		pass

	# 查询某用户的聊天列表
	def test_001_Message_Controller_chat(self):
		self.fp.write('=' * 100 + '\n')
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
		self.fp.write('=' * 100 + '\n')

	# 查询与某人的历史聊天记录(给定时间之前的消息)
	def test_002_User_Controller_backward(self):
		self.fp.write('=' * 100 + '\n')
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
		self.fp.write('=' * 100 + '\n')

	# 查询与某人的历史聊天记录(给定时间之前的消息)
	def test_003_User_Controller_forward(self):
		self.fp.write('=' * 100 + '\n')
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
		self.fp.write('=' * 100 + '\n')


	# 删除和某个用户的私聊信息
	def test_004_User_Controller_delete_withuser(self):
		self.fp.write('=' * 100 + '\n')
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
			sql = {"_id":re.compile(rex)}
			mgresult = mgdb('userMessage:%s.' %memberId, sql, "createTime", -1)
			self.assertEqual(len(mgresult), 0, msg="删除与他人得私聊信息功能正常")
			self.fp.write(f'======删除和某个用户的私聊信息：True======\n')
		except:
			self.fp.write(f'======删除和某个用户的私聊信息：False======\n')
		self.fp.write('=' * 100 + '\n')

	# 用户删除某条私聊消息
	def test_005_User_Controller_delete_message(self):
		self.fp.write('=' * 100 + '\n')
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
		try:
			for data in testData:
				req = User_Controller(self.clientType, self.version).delete_message(token, data)
				if len(data) != 0:
					self.assertEqual(req.status_code, 200)
					for messageid in data:
						sql = {'_id': messageid}
						mgr = mgdb('userMessage:%s.' %memberId, sql, '_id', 1)
						self.assertEqual(len(mgr), 0)
			self.fp.write(f'======用户删除某条私聊消息：True======\n')
		except:
			self.fp.write(f'======用户删除某条私聊消息：False======\n')
		self.fp.write('=' * 100 + '\n')

	# 删除和某个用户的会话框
	def test_006_delete_session_withuser(self):
		self.fp.write('=' * 100 + '\n')
		userInfos = random.choice(read_file(self.tokenfile))
		username = userInfos['username']
		token = "Bearer % s" % (userInfos['token'])
		memberId = Mysql().reslut_replace(f'select id from user where username={username}')
		mgresult = return_mgdb('userMessage:%s.' %memberId)
		# 聊条记录session
		sessionList = mgresult.distinct("sessionId")
		to_userId = str(random.choice(list(range(5152, 5201)) + list(range(5248, 5297))))
		if int(to_userId) > int(memberId):
			rex = f'{memberId}:{to_userId}'
		else:
			rex = f'{to_userId}:{memberId}'
		req = User_Controller(self.clientType, self.version).delete_session_withuser(token, to_userId)
		try:
			assert req.status_code == 200
			self.fp.write(f'======删除和某个用户的会话框：True======\n')
		except:
			self.fp.write(f'======删除和某个用户的会话框：False======\n')
		self.fp.write('=' * 100 + '\n')

	# 查询私聊消息
	def test_007_user_withuser(self):
		"""
		只要ids存在则查询出对应得结果， 如果不存在时，则不返回
		:return:
		"""
		self.fp.write('=' * 100 + '\n')
		userInfos = random.choice(read_file(self.tokenfile))
		username = userInfos['username']
		token = "Bearer % s" % (userInfos['token'])
		memberId = Mysql().reslut_replace(f'select id from user where username={username}')
		to_userId = str(random.choice(list(range(5152, 5201)) + list(range(5248, 5297))))
		if int(to_userId) > int(memberId):
			rex = f'{memberId}:{to_userId}'
		else:
			rex = f'{to_userId}:{memberId}'
		sql = {"_id": re.compile(rex)}
		db = return_mgdb('userMessage:%s.' % memberId)
		messageList = db.find(sql).distinct('_id')
		ids = []
		for messageid in messageList:
			ids.append(messageid.split(":")[-1])
		rightId = random.sample(ids, math.ceil(len(ids)/5))
		datas = [None, rightId, rightId+["-1"]]
		for data in datas:
			req = User_Controller(self.clientType, self.version).withUserId(token, to_userId, data)
			if data == None:
				self.assertNotEqual(req.status_code, 200)
			elif len(data) == 0:
				pass
			else:
				self.assertEqual(req.status_code, 200)
				for mid in data:
					indx = data.index(mid)
					if mid in ids:
						content = db.find({"_id": f"%s:{mid}" % rex}).distinct('content')
						self.assertEqual(f"u'{req.json()[indx]['content']}'", f"u'{content[0]}'")
		self.fp.write('=' * 100 + '\n')

	# 撤销私聊消息
	def test_008_exit_message(self):
		# self.fp.write('=' * 100 + '\n')
		userInfos = random.choice(read_file(self.tokenfile))
		username = userInfos['username']
		token = "Bearer % s" % (userInfos['token'])
		memberId = Mysql().reslut_replace(f'select id from user where username={username}')
		to_userId = str(random.choice(list(range(5152, 5201)) + list(range(5248, 5297))))
		if int(to_userId) > int(memberId):
			rex = f'{memberId}:{to_userId}'
		else:
			rex = f'{to_userId}:{memberId}'
		sql = {"_id": re.compile(rex)}
		db = return_mgdb('userMessage:%s.' % memberId)
		messageList = db.find(sql).distinct('_id')
		ids = []
		for mid in messageList:
			ids.append(mid.split(":")[-1])
		if len(ids) == 0:
			pass
		else:
			messageId = random.choice(ids)
			req = User_Controller(self.clientType, self.version).exit_message(token, to_userId, memberId)
			self.assertEqual(req.status_code , 200)

	def test_009(self):
		self.fp.close()









