# -*- coding: utf-8 -*-
"""
修正v2.0 版本中没有标准化的错误
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

# read data
file = '西昌#2高炉每日整理数据v2.1.xlsx'
path = './result/'
df = pd.read_excel(path+file, sheet_name = '总表', index_col=0)

# 去掉 日产量 燃料比 有缺失得样本
df = df.drop(index=df.index[np.any(df.loc[:,df.columns[0:2]].isna(), axis=1)])
df_std = pd.DataFrame(data=None, index = df.index)
std = StandardScaler()
df_std['日产量'] = std.fit_transform(df[df.columns[0:1]])
df_std['燃料比'] = std.fit_transform(df[df.columns[1:2]])

# # 聚类
kmeans = KMeans(n_clusters=3)
kmeans.fit(df_std)

# 画聚类图
plt.scatter(df.iloc[:,0], df.iloc[:,1],c=kmeans.labels_,cmap='viridis')
plt.colorbar()
plt.xlabel("日产量")
plt.ylabel("燃料比")
plt.savefig("./result/result_20_3_1/3聚类.png")

df['label'] = kmeans.labels_
df['time'] = df.index # 把index 添加到column中 有助于调用sactter()

# draw all the points.
for i in range(0,36):
    df['time'] = df.index
    df.plot.scatter(x='time',y=i,c='label',colormap='viridis')
    plt.title(df.columns[i]+".png")
    plt.savefig('./result/result_20_3_1/3聚类散点图/'+str(i)+".png")
    plt.close()

# # Only draw the best and worst points.
# label0 = df.groupby('label').get_group(0)
# label2 = df.groupby('label').get_group(2)
# for i in range(0,36):
#     plt.scatter(x=label0.time, y=label0.iloc[:,i], label=0)
#     plt.scatter(x=label2.time, y=label2.iloc[:,i], label=2)
#     plt.title(df.columns[i])
#     plt.legend()
#     plt.savefig('./result/BestAndWorst/'+str(i)+".png")
#     plt.close()