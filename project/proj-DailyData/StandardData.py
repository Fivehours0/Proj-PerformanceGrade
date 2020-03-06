"""
对整理好的数据:
西昌#2高炉每日整理数据v2.2.xlsx
进行正态标准化
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

std = StandardScaler()

file = './西昌#2高炉每日整理数据v2.2.xlsx'
df = pd.read_excel(file)

df_std = df.copy()
for i in range(1, df.columns.size):
    # df_std.iloc[:,i] = std.fit_transform(df_std.iloc[:,i:i+1].values) # fit_transfrom 不支持处理有NaN的数据
    arrStd = df_std.iloc[:, i].std()
    arrMean = df_std.iloc[:, i].mean()
    df_std.iloc[:, i] = df_std.iloc[:, i].apply(lambda x: (x-arrMean)/arrStd)

df_std.to_excel("西昌#2高炉每日整理数据v2.2_标准化.xlsx")

