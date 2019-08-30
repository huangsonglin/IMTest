#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/8/9 15:59'

import os, sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
import datetime, time
from until.token import get_token



class Message_Controller():

    def __init__(self, clientType, version):
        self.clientType = clientType
        self.version = version
        self.host = 'http://139.196.57.60:9090'
        self.headers = {'Content-Type':'application/x-www-form-urlencoded',
            'clientType':self.clientType,
            'User-Agent':f'Auction/{self.version} (iPhone; iOS 10.3.3; Scale/2.00)',
            'Connection':'keep - alive'}
        self.timeout = 3

    # 查询聊天列表
    def chat(self, Authorization):
        url = self.host + '/message/user/chat'
        self.headers.update(Authorization=Authorization)
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # 强制退出
    def logout(self, Authorization, userId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/message/user/{userId}/logout'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req


# 聊天室管理
class Chat_Room_Controller():
    def __init__(self, clientType, version):
        self.clientType = clientType
        self.version = version
        self.host = 'http://139.196.57.60:9090'
        self.headers = {'Content-Type':'application/x-www-form-urlencoded',
            'clientType':self.clientType,
            'User-Agent':f'Auction/{self.version} (iPhone; iOS 10.3.3; Scale/2.00)',
            'Connection':'keep - alive'}
        self.timeout = 3

    # 查询聊天室消息 - -查询给定时间之前的消息, 返回数据按时间升序排列, beforeDate 默认系统当前时间
    def backward(self, Authorization, chatRoomId, beforeDate=str(int(time.time())), size=10):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatRoom/backward'
        data = {"chatRoomId": chatRoomId, "beforeDate": beforeDate, "size": size}
        req = requests.get(url, params=data, headers=self.headers, timeout= self.timeout)
        return req

    # 查询聊天室消息--查询给定时间之后的消息,返回数据按时间升序排列
    def forward(self, Authorization, chatRoomId, afterDate, size):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatRoom/forward'
        data = {"chatRoomId": chatRoomId, "afterDate": afterDate, "size": size}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # 查询当前用户所有的聊天室
    def chatRoom(self, Authorization):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatRoom/user/chatRoom'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # 移除黑名单
    def delete_black(self, Authorization, chatRoomId, userId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatRoom/{chatRoomId}/black/{userId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # 加入黑名单
    def add_black(self, Authorization, chatRoomId, userId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatRoom/{chatRoomId}/black/{userId}'
        req = requests.post(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatRoom/{chatRoomId}/user/{userId} 从聊天室踢出用户
    def kick_user(self, Authorization, chatRoomId, userId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatRoom/{chatRoomId}/user/{userId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatRoom/{chatRoomId}/withdraw/{messageId} 撤销聊天室消息
    def withdraw(self, Authorization, chatRoomId, messageId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatRoom/{chatRoomId}/withdraw/{messageId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatRoom/{id} 根据id查询聊天室
    def find_chatRoom(self, Authorization, id):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatRoom/{id}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatRoom/{id}/enter 进入聊天室, 返回最近2分钟内的消息
    def enter_chatRoom(self, Authorization, id):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatRoom/{id}/enter'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatRoom/{id}/exit 退出聊天室
    def exit_chatRoom(self, Authorization, id):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatRoom/{id}/exit'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatRoom/{id}/users 根据聊天室id分页查询聊天室用户列表
    def find_users(self, Authorization, id):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatRoom/{id}/users'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req


# 群组管理 : Chat Group Controlle
class Chat_Group_Controlle:
    def __init__(self, clientType, version):
        self.clientType = clientType
        self.version = version
        self.host = 'http://139.196.57.60:9090'
        self.headers = {'Content-Type':'application/x-www-form-urlencoded',
            'clientType':self.clientType,
            'User-Agent':f'Auction/{self.version} (iPhone; iOS 10.3.3; Scale/2.00)',
            'Connection':'keep - alive'}
        self.timeout = 3

    # POST /chatGroup 创建群
    def chatGroup(self, Authorization, **kwargs):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatGroup'
        req = requests.post(url, data=_data, headers= self.headers, timeout= self.timeout)
        return req

    # GET /chatGroup/backward 查询群消息--查询给定时间之前的消息,返回数据按时间升序排列, beforeDate 默认系统当前时间
    def backward(self, Authorization, groupId, beforeDate, size):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatGroup/backward'
        data = {'groupId': groupId, "beforeDate": beforeDate, "size": size}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatGroup/forward 查询群消息--查询给定时间之后的消息,返回数据按时间升序排列
    def forward(self, Authorization, groupId, afterDate, size):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatGroup/forward'
        data = {'groupId': groupId, "afterDate": afterDate, "size": size}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # POST /chatGroup/update 修改群
    def update(self, Authorization, **kwargs):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatGroup/update'
        req = requests.post(url, data=_data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatGroup/user 查询当前用户所有群组
    def user(self, Authorization):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatGroup/user'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # 加入群


    # GET /chatGroup/user/group/delete 用户删除群聊消息
    def delete(self, Authorization, messageIds):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/chatGroup/user/group/delete'
        data = {'messageIds': messageIds}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatGroup/{groupId} 查询群消息
    def chatGroup(self, Authorization, groupId, ids):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatGroup/{groupId}'
        data = {'ids': ids}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatGroup/{groupId}/black/{userId} 移除黑名单
    def dele_balck(self, Authorization, groupId, userId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatGroup/{groupId}/black/{userId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    def add_balck(self, Authorization, groupId, userId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatGroup/{groupId}/black/{userId}'
        req = requests.post(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatGroup/{groupId}/user/{userId} 退群
    def quit(self, Authorization, groupId, userId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatGroup/{groupId}/user/{userId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatGroup/{groupId}/withdraw/{messageId} 撤销群消息
    def withdraw(self, Authorization, groupId, messageId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatGroup/{groupId}/withdraw/{messageId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatGroup/{id} 根据id查询群
    def find(self, Authorization, id):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatGroup/{id}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /chatGroup/{id}/users 根据群id分页查询群用户列表
    def find_users(self, Authorization, id, page=1, rows=10):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/chatGroup/{id}/users'
        data = {"page": page, "rows": rows}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

# 用户好友管理 : User Controller
class User_Controller:
    def __init__(self, clientType, version):
        self.clientType = clientType
        self.version = version
        self.host = 'http://139.196.57.60:9090'
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'clientType': self.clientType,
                        'User-Agent': f'Auction/{self.version} (iPhone; iOS 10.3.3; Scale/2.00)',
                        'Connection': 'keep - alive'}
        self.timeout = 3

    # POST /user/add 添加好友
    def add(self, Authorization, friendId):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/user/add'
        data = {"friendId": friendId}
        req = requests.post(url, data=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/backward 查询和用户的聊天消息--查询给定时间之前的消息,返回数据按时间升序排列, beforeDate 默认系统当前时间
    def backward(self, Authorization, userId, beforeDate=None, size=20):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/user/backward'
        data = {"userId": userId, "beforeDate": beforeDate, "size": size}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # POST /user/createChatGroup 拉好友创建群(不需要传当前用户id)
    def createChatGroup(self, Authorization, userIds):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/user/createChatGroup'
        data = {'userIds': userIds}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/delete/{withUserId} 删除和某个用户的私聊信息
    def delete_withuser(self, Authorization, withUserId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/user/delete/{withUserId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/forward 查询和用户的聊天消息--查询给定时间之后的消息,返回数据按时间升序排列
    def forward(self, Authorization, userId, afterDate, size=20):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/user/backward'
        data = {"userId": userId, "afterDate": afterDate, "size": size}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/list 分页查询当前用户好友列表
    def list(self, Authorization, page=1, rows=10):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/user/list'
        data = {"page": page, "rows": rows}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/session/delete/{withUserId} 删除和某个用户的会话框
    def delete_session_withuser(self, Authorization, withUserId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/user/session/delete/{withUserId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/user/delete 用户删除私聊信息
    def delete_message(self, Authorization, messageIds):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/user/user/delete'
        data = {"messageIds": messageIds}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/users 分页查询注册的所有用户
    def users(self, Authorization, page=1, rows=10):
        self.headers.update(Authorization=Authorization)
        url = self.host + '/user/users'
        data = {"page": page, "rows": rows}
        req = requests.get(url, params=data, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/{withUserId} 查询私聊消息
    def withUserId(self, Authorization, withUserId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/user/{withUserId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req

    # GET /user/{withUserId}/withdraw/{messageId} 撤销私聊消息
    def exit_message(self, Authorization, withUserId, messageId):
        self.headers.update(Authorization=Authorization)
        url = self.host + f'/user/{withUserId}/withdraw/{messageId}'
        req = requests.get(url, headers=self.headers, timeout=self.timeout)
        return req



if __name__ == '__main__':
    token = 'Bearer ' + 'ba6e50d3-fc93-43bc-b3f9-a3d1f9dbf475'
    systime_timestamp = int(datetime.datetime.now().timestamp() * 1000)
    result = User_Controller('IOS', '5.0.0').delete_message(token, ["5141:5256:10"])
    print(result.status_code, result.text)
