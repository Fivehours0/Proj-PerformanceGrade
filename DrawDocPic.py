# -*- coding: utf-8 -*-
# 绘制高炉操作参数的稳定性范围提取方法的插图
# 1. 数据预处理的插图
# 2. 指标重要性排序的插图, 随机森林
# 3. 聚类图, 散点图

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
def outlier():
    # 异常值画图
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
    return None
plt.rcParams['font.sans-serif']=['SimHei'] # 修复图片不显示中文的问题
plt.rcParams['axes.unicode_minus']=False

## 随机森林图, 搁置

file = '西昌#2高炉每日整理数据v2.0.xlsx'

path = './result/'
df = pd.read_excel(path+file, sheet_name=0, index_col=0)


from sklearn.cluster import KMeans
x = df.iloc[:,:2].dropna()
kmeans = KMeans(n_clusters=3)
kmeans.fit(x)

y = kmeans.labels_


# plt.scatter(x=x.iloc[:,0], y=x.iloc[:,1],c=kmeans.labels_)

x['label'] = y
df['label'] = x['label']
df2 = df.dropna()
from sklearn.ensemble import RandomForestClassifier

forest = RandomForestClassifier(n_estimators=5, random_state=2)


forest.fit(df2.iloc[:,:30],df2.iloc[:,30])



imp = forest.feature_importances_
plt.barh(range(30),imp)
plt.yticks(np.arange(30), df2.iloc[:,:30].columns)     
plt.xlabel("Feature importance")     
plt.ylabel("Feature") 





