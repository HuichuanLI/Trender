# -*- coding:utf-8 -*-
# @Time : 2022/2/5 6:14 下午
# @Author : huichuan LI
# @File : stock.py
# @Software: PyCharm
from jqdatasdk import *
import time
import pandas as pd
import datetime
import os
auth('17621171968','171968')
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

df = get_price ('000001.XSHE', count=100, end_date='2021-01-31', frequency='daily')
print(df)