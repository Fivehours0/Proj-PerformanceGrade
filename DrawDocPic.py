# -*- coding: utf-8 -*-
# 绘制高炉操作参数的稳定性范围提取方法的插图
# 1. 数据预处理的插图
# 2. 指标重要性排序的插图, 随机森林
# 3. 聚类图, 散点图

import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei'] # 修复图片不显示中文的问题
plt.rcParams['axes.unicode_minus']=False

param = '炉顶温度1'
file_name = '西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl'
path = './data/西昌2#高炉数据19年10-11月/pkl/'

df = pd.read_pickle(path+file_name)



df = df.groupby('采集项名称').get_group(param)
# 数据格式化
df['业务处理时间'] = df['业务处理时间'].apply(pd.to_datetime)
df['采集项值'] = df['采集项值'].apply(pd.to_numeric)
df = df[['业务处理时间','采集项值']]
df.set_index('业务处理时间', inplace=True)

plt.figure(1)
df.plot()
plt.title('未进行异常分析的数据波动图')

plt.figure(2)
df_after = df.copy()
df_after['采集项值'][df_after['采集项值'] > 1e7] = None
df_after.plot()
plt.title('进行异常分析后的数据波动图')

