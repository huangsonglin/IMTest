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
from case.test_tcp_case import *
from case.test_http_api_case import *

if __name__ == '__main__':
	wirte_token.tokenList()
	# time.sleep(5)
	# Result_concurrent_testing(10000, 0, 1)
	# suit = unittest.TestLoader().loadTestsFromTestCase(Test_http_api)
	# suit = unittest.TestSuite(suit)
	# unittest.TextTestRunner(verbosity=2).run(suit)