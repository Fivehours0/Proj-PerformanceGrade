# -*- coding: utf-8 -*-
'''
# 根据按照天统计的数据，根据高炉稳定性指标（焦比或者综合焦比、透气性、铁水产量、
# 煤气利用率等），从数据分析的角度来提取各关键参数的5个区间？可以考虑用聚类算法来
# 处理。至于这几个指标本身的区间，可以通过统计的方法将其划分为5个区间
'''
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

file = '西昌#2高炉每日整理数据v2.0.xlsx'
path = './result/'

df18 = pd.read_excel(path+file, sheet_name = '18年数据', index_col=0)
df19 = pd.read_excel(path+file, sheet_name = '19年10月-20年2月', index_col=0)
df = pd.concat([df18, df19])

# 去掉 日产量 燃料比 有缺失得样本
df = df.drop(index=df.index[np.any(df.loc[:,df.columns[0:2]].isna(), axis=1)])

x = df.iloc[:,:2]


kmeans = KMeans(n_clusters=3)
kmeans.fit(x)
y = kmeans.labels_

plt.scatter(x=x.iloc[:,0], y=x.iloc[:,1],c=y,cmap='viridis')
plt.colorbar()
plt.savefig("./result/5划分/聚类.png")
df['label'] = y

# for i in range(0,36):
#     df['time'] = df.index
#     df.plot.scatter(x='time',y=i,c='label',colormap='viridis')
#     plt.title(df.columns[i]+".png")
#     plt.savefig('./result/5划分/'+str(i)+".png")
#     plt.close()














