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


global File
File = file
send_result_file = rootPath + r'\TestData\send_data.txt'
recv_result_file = rootPath + r'\TestData\recv_data.txt'
result_file = rootPath + r'\TestData\result.txt'
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
        send_message = "$_".encode() + length(len(message)) + message +"_$".encode()
        self.client.send(send_message)
        recv_data = self.client.recv(self.client.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))
        recv_data = recv_data[2:-2].split(b'\x00\x00\x00')[1].replace(b'%"',  b'\n')
        self.proto_message.ParseFromString(recv_data)
        result = repaly_link_receve(self.proto_message)

    # send message
    def Send(self, fromusername, contentType, contentTxt, touserId, clientType):
        message = Message_Protobuf(File).send(fromusername, contentType, contentTxt, touserId, clientType)
        send_message = "$_".encode() + length(len(message)) + message + "_$".encode()
        befortime = time.time()
        self.client.sendall(send_message)
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
        result.update(Responsetime= round(responsetime, 2))
        file = open(self.datafile, 'a', encoding='utf-8')
        file.write(u'%s' % str(result))
        file.write('\n')
        file.close()

    # analysis recv data
    def analysis_data(self):
        data = self.client.recv(self.length)
        FRIST_DATA = b''
        SECOND_DATA = b''
        NUM_START = data.count(Start)
        NUM_END = data.count(End)
        if data[:2] == Start and data[-2:] == End and NUM_END == NUM_START == 1:
            if b'HEARTBEAT_ACK' not in data:
                recv_data = data[6:-2]
                self.proto_message.ParseFromString(recv_data)
                result = replay_send_receve(self.proto_message)
            else:
                recv_data = data[6:-2]
                self.proto_message.ParseFromString(recv_data)
                result = heart_receve(self.proto_message)
        elif NUM_START == NUM_END and NUM_START >= 2:
            NUM = 0
            for i in range(NUM_START):
                temp = NUM
                NUM = data.find(Start, NUM + 1)
                if i != NUM_START - 1:
                    recv_data = data[temp: NUM]
                else:
                    recv_data = data[temp: NUM] + b'$'
                recv_data = recv_data[6:-2]
                if b'HEARTBEAT_ACK' not in recv_data:
                    self.proto_message.ParseFromString(recv_data)
                    result = replay_send_receve(self.proto_message)
                else:
                    self.proto_message.ParseFromString(recv_data)
                    result = heart_receve(self.proto_message)
        else:
            if NUM_START == 1 and NUM_END == 0:
                FRIST_DATA = data
                pass
            elif NUM_START == NUM_END == 0:
                pass
            else:
                SECOND_DATA = data
                recv_data = FRIST_DATA + SECOND_DATA
                recv_data = recv_data[6:-2]
                if b'HEARTBEAT_ACK' not in recv_data:
                    self.proto_message.ParseFromString(recv_data)
                    result = replay_send_receve(self.proto_message)
                else:
                    self.proto_message.ParseFromString(recv_data)
                    result = heart_receve(self.proto_message)
        return result

    # Send Heartbeat
    def heartbeat(self, username):
        message = Message_Protobuf(File).HEARTBEAT(username, "IOS")
        send_message = "$_".encode() + length(len(message)) + message + "_$".encode()
        self.client.send(send_message)
        data = self.client.recv(self.length)

    # recv meassage
    def Recv(self, username, num):
        Start = b'$_'
        End = b'_$'
        pool = ThreadPoolExecutor(max_workers=num)
        threads = []
        self.Link(username)
        btime = time.time()
        while True:
            sf = open(self.recv_datafile, 'a', encoding='utf-8')
            beforetime = time.time()
            f = pool.submit(self.client.recv, self.length)
            aftertime = time.time()
            data = f.result()
            threads.append(f)
            recvtime = round((aftertime - beforetime) * 1000, 2)
            if not data:
                break
            else:
                recv_data = data[6: -2]
                try:
                    # 心跳内容
                    if b'HEARTBEAT_ACK' not in recv_data:
                        try:
                            self.proto_message.ParseFromString(recv_data)
                            result = replay_send_receve(self.proto_message)
                            result.update(Responsetime=recvtime)
                            sf.write(str(result))
                        except:
                            pass
                    else:
                        try:
                            self.proto_message.ParseFromString(recv_data)
                            result = heart_receve(self.proto_message)
                            result.update(Responsetime=recvtime)
                            sf.write(str(result))
                        except:
                            pass
                finally:
                    sf.write('\n')
            atime = time.time()
            sendHerat = (int(atime) - int(btime))
            # 每48秒发送一次心跳
            if sendHerat % 48 == 0 and sendHerat != 0:
                self.heartbeat(username)
                btime = atime + 1
            sf.close()
        wait(threads)
        self.close()

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
    pool = ThreadPoolExecutor(max_workers=concurrentNum)
    futures = []
    for i in range(concurrentNum):
        TXT = [chineseText(random.randint(1, 3288)),
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
        f1 = pool.submit(Function().Send, fromuser, contenType, content, int(memberId), "IOS")
        futures.append(f1)
    wait(futures)

# 多线程并发压力测试函数
def Function_thread_testing(threaNum, internTime, duration):
    threads = []
    tousername = random.randint(40000000000, 40000000049)
    memberId = Mysql().reslut_replace(f'select id from user where username={tousername}')
    recvThread =  threading.Thread(target=Function().Recv, args=(tousername, threaNum))
    threads.append(recvThread)
    sendThread = threading.Thread(target=Function_concurrent_sendmessage, args=(threaNum, tousername ))
    threads.append(sendThread)
    for t in threads:
        t.setDaemon(True)
        t.start()
        time.sleep(internTime)
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
    recvTimeList = []
    sendTimeList = []
    heartTimeList = []
    for data in data_send:
        if data['Code'] == 200:
            data_send_success_list.append(data)
            sendTimeList.append((data['content']['MessageId'], round(float(data['Responsetime']), 2)))
    for data in data_recv:
        if "HEARTBEAT_ACK" in list(data.values()):
            heartTimeList.append(data)
        else:
            recvTimeList.append((data['content']['MessageId'], round(float(data['Responsetime']), 2)))
    # 是否漏发漏收
    isintegrity = (len(data_send_success_list) == len(data_recv))
    # 发送消息成功百分比
    successrate = '%.2f' % (len(data_send_success_list) / len(data_send) * 100)
    # 发送消息失败百分比
    errorrate =  '%.2f' % ((len(data_send) - len(data_send_success_list)) / len(data_send) * 100)
    # 接发收总时间
    totalList = []
    for Sdata in sendTimeList:
        for Rdata in recvTimeList:
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
    recvDF = pd.DataFrame(np.array(recvTimeList), columns=header)
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
                f'Message sent successfully: {len(data_send_success_list)}; Message received successfully: {len(data_recv)}\n'
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


