#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/7 17:07'

import time
import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import random
import json
from temp.message_pb2 import Message, MessageContent
from until.mysql import Mysql
from until.token import get_token
from google.protobuf.json_format import MessageToJson
from concurrent.futures import ThreadPoolExecutor, wait

file = rootPath + r'\TestData\token.txt'
class wirte_token:
    global TokenList
    TokenList = []

    def tokenList():
        threads = []
        pool = ThreadPoolExecutor(max_workers=50)
        for username in range(40000000000, 40000000050):
            f = pool.submit(get_token, username, 123456)
            threads.append(f)
            Token = f.result()
            TokenList.append({"token": "%s" % Token, "username": "%d" % username})
        wait(threads)
        with open(file, 'w') as f:
            for tokenInfo in TokenList:
                f.write(str(tokenInfo))
                f.write('\n')

    def random_token():
        TokenInfo = random.choice(TokenList)
        return TokenInfo

def repaly_link_receve(message):
    messageType = message.messageType
    code = message.code
    message = message.message
    # systemTime = message.systemTime
    result = {"messageType": messageType, "code": code, "message": message}
    return result

def content_receve(message):
    MessageId = message.id
    content = message.content
    contentType = message.contentType
    createTime = message.createTime
    userId = message.userId
    userName = message.userName
    userIcon = message.userIcon
    result = {"MessageId": MessageId, "content": content, "contentType": contentType, "createTime": createTime,
              "userId": userId, "userName": userName, "userIcon": userIcon}
    return result

def replay_send_receve(message):
    messageType = (message.messageType)
    destinationId = (message.destinationId)
    # content = content_receve(messageContent)
    content = message.content
    msg = MessageContent()
    msg.ParseFromString(content)
    content = content_receve(msg)
    destinationType = (message.destinationType)
    path = (message.path)
    clientType = (message.clientType)
    authorization = (message.authorization)
    result = {"messageType": messageType, "destinationId": destinationId, "content": content,
              "destinationType": destinationType, "path": path, "clientType": clientType, "authorization": authorization}
    return result

def heart_receve(message):
    messageType = message.messageType
    result = {'messageType': messageType}
    return result

class Message_Protobuf():

    def __init__(self, file):
        if os.path.exists(file):
            self.file = file
            self.tokenList = []
            with open(self.file) as f:
                for line in f.readlines():
                    line = line.replace('\n', '').replace("'", '"')
                    json_data = json.loads(line)
                    self.tokenList.append(json_data)
        else:
            raise FileExistsError('文件不存在')

    # 请求链接protobuf
    def link(self, username, clientType):
        """
        :param username:    Request the linker account
        :param clientType:  device type. "ANDRIOD" or "IOS"
        :return:            protobuf data
        """
        index = abs(int(username) - 40000000000)
        message = Message()
        message.messageType = "CONNECT"
        message.authorization = self.tokenList[index]['token']
        message.clientType = clientType
        message.systemTime = int(time.time()*1000)
        proto_message = message.SerializeToString()
        return proto_message

    def send(self, fromusername, contentType, contentTxt, touserId, clientType):
        """
        :param fromusername:    Message sender's username
        :param contentType:     message type. "TXT" or "IMG"
        :param contentTxt:      message area
        :param touserId:        message recverId
        :return:
        """
        index = abs(int(fromusername) - 40000000000)
        userInfos = Mysql().sql_result(f'select id, name, icon from user where username={fromusername}')
        mcontent = MessageContent()
        message = Message()
        mcontent.content = contentTxt
        mcontent.contentType = contentType
        mcontent.userId = userInfos[0][0]
        mcontent.userName = userInfos[0][1]
        mcontent.userIcon = userInfos[0][2]
        contentTxt = mcontent.SerializeToString()
        message.messageType = "MESSAGE"
        message.destinationId = touserId
        message.content = contentTxt
        message.destinationType = "TO_USER"
        message.path = "sendMessage"
        message.clientType = clientType
        message.authorization = self.tokenList[index]['token']
        proto_message = message.SerializeToString()
        return proto_message

    def HEARTBEAT(self, username, clientType):
        index = abs(int(username) - 40000000000)
        message = Message()
        message.messageType = "HEARTBEAT"
        message.authorization = self.tokenList[index]['token']
        message.clientType = clientType
        proto_message = message.SerializeToString()
        return proto_message


# message = Message_Protobuf(File).send(fromusername, contentType, contentTxt, touserId, clientType)