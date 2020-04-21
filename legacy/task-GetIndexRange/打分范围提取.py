# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:02:34 2020

@author: Administrator
"""

# 根据按照天统计的数据，根据高炉稳定性指标（焦比或者综合焦比、透气性、铁水产量、
# 煤气利用率等），从数据分析的角度来提取各关键参数的5个区间？可以考虑用聚类算法来
# 处理。至于这几个指标本身的区间，可以通过统计的方法将其划分为5个区间
import pandas as pd
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
# from sklearn.datasets import make_blobs 

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

df18 = pd.read_excel('西昌#2高炉每日整理数据.xlsx', sheet_name = 1,
                    header = 0,skiprows=[1,2])
df19 = pd.read_excel('西昌#2高炉每日整理数据.xlsx', sheet_name = 2, 
                    header = 0,skiprows=[1])

df = pd.concat([df18, df19]).reset_index(drop=True)

X = df.iloc[:317,1:3].dropna()
kmeans = KMeans(n_clusters=5)
kmeans.fit(X)
X['label'] = kmeans.labels_

tmp = tmp = X.iloc[:,0:2]
tmp.plot.scatter(x=0, y=1,c=kmeans.labels_,colormap='viridis')

df_merge = pd.merge(df, X,left_index=True,right_index=True,how='inner')
# df_group = {}
# df_group[0] = df_merge.groupby('label').get_group(0)
# df_group[1] = df_merge.groupby('label').get_group(1)
# df_group[2] = df_merge.groupby('label').get_group(2)
# df_group[3] = df_merge.groupby('label').get_group(3)
# df_group[4] = df_merge.groupby('label').get_group(4)

for i in range(1,47):
    if not pd.isna(df_merge.iloc[0,i]):
        df_merge.plot.scatter(x=0,y=i,c='label',colormap='viridis')
        plt.savefig(str(i)+".png")
        plt.close()

# 新需求
# 分三类只标注第一类和第三类，第二类不要显示，

