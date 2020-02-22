# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 22:23:53 2020

@author: Administrator
"""
import pandas as pd
file = '西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl'
df = pd.read_pickle('./'+file)