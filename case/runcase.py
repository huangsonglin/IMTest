#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/9/3 10:18'

import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import unittest
from case.TestCase import *
from case.HttpTestCase import *

if __name__ == '__main__':
	wirte_token.tokenList()
	time.sleep(5)
	Result_concurrent_testing(2000, 0.05, 60)
	suit = unittest.TestLoader().loadTestsFromTestCase(unitest_http_api)
	suit = unittest.TestSuite(suit)
	unittest.TextTestRunner(verbosity=2).run(suit)