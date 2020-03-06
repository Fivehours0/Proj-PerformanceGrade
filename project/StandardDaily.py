"""
对整理好的数据:
西昌#2高炉每日整理数据v2.2.xlsx
进行正态标准化
"""
import pandas as pd
from sklearn.preprocessing import StandardScaler

std = StandardScaler()

file = './result/西昌#2高炉每日整理数据v2.2.xlsx'
df = pd.read_excel(file)

df_std = pd.DataFrame(data=None, index=df.ilc[:, 0])

std.fit_transform(df[df.columns[1:2]])


