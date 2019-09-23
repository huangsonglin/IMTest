#!user/bin/python
# -*- coding: utf-8 -*-
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

global File
File = file
send_result_file = rootPath + r'\TestData\send_data.txt'
recv_result_file = rootPath + r'\TestData\recv_data.txt'
result_file = rootPath + r'\TestData\result.txt'
wrong_data_file = rootPath + r'\TestData\wrong.txt'
host = "139.196.57.60"
# host = "192.168.50.115"
port = 9999


class Function():

	def __init__(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect((host, port))
		self.datafile = send_result_file
		self.recv_datafile = recv_result_file
		self.proto_message = Message()
		self.proto_messageContent = MessageContent()
		self.length = self.client.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

	# close client
	def close(self):
		self.client.close()

	# request tcp_link
	def Link(self, username):
		message = Message_Protobuf(File).link(username, "IOS")
		send_message = "$_".encode() + length(len(message)) + message + "_$".encode()
		self.client.send(send_message)
		# recv_data = self.client.recv(self.client.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))
		# recv_data = recv_data[6:-2]
		# self.proto_message.ParseFromString(recv_data)
		# result = repaly_link_receve(self.proto_message)


	# analysis recv data
	def analysis_data(self, data):
		Start = b'$_'
		End = b'_$'
		FRIST_DATA = b''
		SECOND_DATA = b''
		NUM_START = data.count(Start)
		NUM_END = data.count(End)
		ResultList = []
		# 正常接收的数据
		if data[:2] == Start and data[-2:] == End and NUM_END == NUM_START == 1:
			if b'CONNECT_ACK' in data:
				recv_data = data[6:-2]
				self.proto_message.ParseFromString(recv_data)
				result = repaly_link_receve(self.proto_message)
			elif b'MESSAGE' in data:
				recv_data = data[6:-2]
				self.proto_message.ParseFromString(recv_data)
				result = replay_send_receve(self.proto_message)
			elif b'HEARTBEAT_ACK' in data:
				recv_data = data[6:-2]
				self.proto_message.ParseFromString(recv_data)
				result = heart_receve(self.proto_message)
			else:
				result = data
			ResultList.append(result)
			return ResultList
		else:
			wf = open(wrong_data_file, 'a+')
			dataList = data.split(b'$_')
			if dataList[0] == b'':
				dataList.remove(dataList[0])
			if dataList[-1] == b'':
				dataList.remove(dataList[-1])
			for i in range(len(dataList)):
				if i == 0:
					if data.startswith(Start):
						dataList[0] = Start + dataList[0]
				else:
					if i == len(dataList)-1:
						endnum = dataList[i].find(End)
						writedata = dataList[i][endnum + 2:]
						if writedata != b'':
							wf.write(str(dataList[i][endnum + 2:]) + '\n')
						dataList[i] = Start + dataList[i][0:endnum + 2]
						wf.close()
					else:
						dataList[i] = Start + dataList[i]
			for data in dataList:
				if b'CONNECT_ACK' in data:
					recv_data = data[6:-2]
					self.proto_message.ParseFromString(recv_data)
					result = repaly_link_receve(self.proto_message)
				elif b'MESSAGE' in data:
					recv_data = data[6:-2]
					self.proto_message.ParseFromString(recv_data)
					result = replay_send_receve(self.proto_message)
				elif b'HEARTBEAT_ACK' in data:
					recv_data = data[6:-2]
					self.proto_message.ParseFromString(recv_data)
					result = heart_receve(self.proto_message)
				else:
					result = data
				ResultList.append(result)
			return ResultList

	# send message
	def Send(self, fromusername, contentType, contentTxt, touserId, clientType):
		message = Message_Protobuf(File).send(fromusername, contentType, contentTxt, touserId, clientType)
		send_message = "$_".encode() + length(len(message)) + message + "_$".encode()
		befortime = time.time()
		self.client.send(send_message)
		recv_data = self.client.recv(self.length)
		aftertime = time.time()
		recv_data = recv_data[6: -2]
		self.proto_message.ParseFromString(recv_data)
		result = replay_send_receve(self.proto_message)
		# 毫秒级
		responsetime = (aftertime - befortime) * 1000
		if result['destinationId'] != 0:
			code = 200
		else:
			result = repaly_link_receve(self.proto_message)
			code = result['code']
		result.update(Code=code)
		result.update(Responsetime=round(responsetime, 2))
		file = open(self.datafile, 'a', encoding='utf-8')
		file.write(u'%s' % str(result))
		file.write('\n')
		file.close()

	# Send Heartbeat
	def heartbeat(self, username):
		message = Message_Protobuf(File).HEARTBEAT(username, "IOS")
		send_message = "$_".encode() + length(len(message)) + message + "_$".encode()
		self.client.send(send_message)
		data = self.client.recv(self.length)
		self.proto_message.ParseFromString(data[6:-2])
		result = heart_receve(self.proto_message)


	# recv meassage
	def Recv(self, username):
		"""
		逻辑：A用户给B用户发消息，服务端收到A的消息，反馈message_ack,表示服务器接收成功，A端上收到message_ack，标记发送成功，
		服务器转发消息给B，B标记以读，说明发送成功，如果B没有标记以读，我后台就会补发
		结果：接收的消息存在重复性
		"""
		End = b'_$'
		self.Link(username)
		btime = time.time()
		while True:
			sf = open(self.recv_datafile, 'a', encoding='utf-8')
			beforetime = time.time()
			data = self.client.recv(self.length)
			aftertime = time.time()
			recvtime = round((aftertime - beforetime) * 1000, 2)
			if not data:
				break
			else:
				# recv_data = data[6: -2]
				# try:
				# 	# 心跳内容
				# 	if b'HEARTBEAT_ACK' not in recv_data:
				# 		try:
				# 			self.proto_message.ParseFromString(recv_data)
				# 			result = replay_send_receve(self.proto_message)
				# 			result.update(Responsetime=recvtime)
				# 			sf.write(str(result))
				# 		except:
				# 			sf.write(str(recv_data))
				# 	else:
				# 		try:
				# 			self.proto_message.ParseFromString(recv_data)
				# 			result = heart_receve(self.proto_message)
				# 			result.update(Responsetime=recvtime)
				# 			sf.write(str(result))
				# 		except:
				# 			sf.write(str(recv_data))
				# finally:
				# 	sf.write('\n')
				resultList = self.analysis_data(data)
				for result in resultList:
					result.update(Responsetime=round(recvtime/len(resultList),2))
					sf.write(str(result) + '\n')
			atime = time.time()
			sendHerat = (int(atime) - int(btime))
			# 每48秒发送一次心跳
			if sendHerat % 48 == 0 and sendHerat != 0:
				self.heartbeat(username)
				btime = atime + 1
			sf.close()
		self.close()


# 多线程并发压力测试函数
def Function_thread_testing(threaNum, internTime, duration):
	threads = []
	tousername = random.randint(40000000000, 40000000049)
	memberId = Mysql().reslut_replace(f'select id from user where username={tousername}')
	for i in range(threaNum):
		TXT = [chineseText(random.randint(1, 100)),
			   ''.join(random.sample(list(emoji.unicode_codes.EMOJI_UNICODE.values()), 10)),
			   get_img()]
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
		recvThread = threading.Thread(target=Function().Recv, args=(tousername, ))
		sendThread = threading.Thread(target=Function().Send, args=(fromuser, contenType, content, int(memberId), "IOS"))
		recvThread.setDaemon(True)
		sendThread.setDaemon(True)
		recvThread.start()
		sendThread.start()
		time.sleep(internTime)
		threads.append(recvThread)
		threads.append(sendThread)
	for t in threads:
		t.join(duration)


# 多线程并发压力测试结果分析
def Result_concurrent_testing(threadnum, internTime, duration):
	with open(send_result_file, 'w') as sf:
		sf.truncate()
	with open(recv_result_file, 'w') as rf:
		rf.truncate()
	with open(result_file, 'w') as ref:
		ref.truncate()
	systime = datetime.datetime.now()
	endtime = systime + datetime.timedelta(seconds=duration)
	while (systime <= endtime):
		Function_thread_testing(threadnum, internTime, duration)
		systime = datetime.datetime.now()
	data_send = read_file(send_result_file)
	data_recv = read_file(recv_result_file)
	data_send_success_list = []
	recv_send_success_list = []
	recvTimeList = []
	sendTimeList = []
	heartTimeList = []
	for data in data_send:
		if data['Code'] == 200:
			data_send_success_list.append(data)
			sendTimeList.append((data['content']['MessageId'], round(float(data['Responsetime']), 2)))
	destinationId = data_send_success_list[0]['destinationId']
	LinkData = []
	RecvMessage = []
	for data in data_recv:
		if "HEARTBEAT_ACK" in list(data.values()):
			heartTimeList.append(data)
		elif data['messageType'] == 'MESSAGE':
			RecvMessage.append(data)
			recvTimeList.append((data['content']['MessageId'], round(float(data['Responsetime']), 2)))
		else:
			pass
	RECVLIST = []
	for recv in recvTimeList:
		if recv[0] not in str(RECVLIST):
			RECVLIST.append(recv)
	# 是否漏发漏收
	isintegrity = (len(data_send_success_list) == len(RECVLIST))
	# 发送消息成功百分比
	successrate = '%.2f' % (len(data_send_success_list) / len(data_send) * 100)
	# 发送消息失败百分比
	errorrate = '%.2f' % ((len(data_send) - len(data_send_success_list)) / len(data_send) * 100)
	# 接发收总时间
	totalList = []
	for Sdata in sendTimeList:
		for Rdata in RECVLIST:
			if Sdata[0] == Rdata[0]:
				totalList.append((Sdata[0], round(Sdata[1] + Rdata[1], 2)))
	# 发送数据结果
	header = ['messgId', 'responseTime']
	sendDF = pd.DataFrame(np.array(sendTimeList), columns=header)
	sendDF[['responseTime']] = sendDF[['responseTime']].apply(pd.to_numeric)
	sendResult = sendDF.describe()
	send_sumTime = sendDF['responseTime'].sum()
	sendResult = (sendResult.rename(columns={'responseTime': ''}))
	# 接收数据结果
	recvDF = pd.DataFrame(np.array(RECVLIST), columns=header)
	recvDF[['responseTime']] = recvDF[['responseTime']].apply(pd.to_numeric)
	recvResult = recvDF.describe()
	recv_sumTime = recvDF['responseTime'].sum()
	recvResult = (recvResult.rename(columns={'responseTime': ''}))
	t1 = []
	t2 = []
	lowrecv = []
	for data in sendTimeList:
		t1.append(data[0])
	for data in recvTimeList:
		t2.append(data[0])
	for data in t1:
		if data not in t2:
			lowrecv.append(data)
	# 发送和接受总数据结果
	totalDF = pd.DataFrame(np.array(totalList), columns=header)
	totalDF[['responseTime']] = totalDF[['responseTime']].apply(pd.to_numeric)
	TotalResult = totalDF.describe()
	total_sumTime = totalDF['responseTime'].sum()
	TotalResult = (TotalResult.rename(columns={'responseTime': ''}))
	with open(result_file, 'w+') as f:
		f.write(f'EXECUTE TIME:{datetime.datetime.now()}\n'
				f'When thread is: {threadnum}, Duration is:{duration} seconds, WaitTime is: {internTime} seconds and send area is txt.\n'
				f'Message sent successfully: {len(data_send_success_list)}; Message received successfully: {len(RECVLIST)}\n'
				f'Whether messages sent and received are lost: {isintegrity}\n'
				f'The total running time is: {total_sumTime} ms\n'
				f'The total sending time is {send_sumTime} ms\n'
				f'The total time accepted is {recv_sumTime} ms.')
		f.write('\n')
		f.write(f'Because of thread receiving problem (data receiving after heartbeat is sent misses), '
				f'the missed message is always: {len(lowrecv)} \n,the missed message id is:'
				f"{'; '.join(lowrecv)}")
		f.write('\n')
		f.write('Data analysis of receiving, sending and receiving information is as follows:')
		f.write(str(TotalResult))
		f.write('\n')
		f.write('Send message data is analyzed as follows:')
		f.write(str(sendResult))
		f.write('\n')
		f.write('Recv message data is analyzed as follows:')
		f.write(str(recvResult))
		f.write('\n')





