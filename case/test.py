#!user/bin/python
#-*- coding: utf-8 -*-
import os
import csv
import numpy as np
import pandas as pd
import json
import emoji
import random

import multiprocessing as mp

def foo(q):
    q.put('hello')

a = ['1','2','3','4']
print('; '.join(a))