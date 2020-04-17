"""
需求：

把新的数据用红色表示，原来的数据用蓝色表示，把它们在燃料比和利用系数的空间中画一下，发给我

"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

FILE = 'data/铁次结果_5h滞后处理v3.0_tc.xlsx'

df = pd.read_excel(FILE, index_col=0)

# 处理 数据中有 inf 的情况 去除掉
df[df == np.inf] = np.nan
df = df.dropna()  # 去除

df = df.iloc[:, :2]
iron_id = 20129937
df_old = df.loc[:iron_id, :]
df_new = df.loc[iron_id:, :]

plt.figure()
plt.scatter(df_old.iloc[:, 0], df_old.iloc[:, 1], c='blue', label='老数据')
plt.scatter(df_new.iloc[:, 0], df_new.iloc[:, 1], c='red' , label='新数据')
# df_old.plot.scatter
# df_new.plot.scatter(0, 1)

plt.xlabel(df.columns[0])
plt.ylabel(df.columns[1])
plt.title('二维散点分布图')
plt.legend()
plt.show()
# plt.figure()
# for j in range(n_clusters):
#     temp = X.groupby('label').get_group(j)
#     temp2 = origin.groupby('label').get_group(j)
#     plt.scatter(temp['混合'], temp2[name], c=COLORS[j], label=j)
#
# plt.xlabel("{:.2f}*日产量+{:.2f}*燃料比*(-1)".format(ALPHA, 1 - ALPHA))
# plt.ylabel(name)
# plt.title(name + "2D聚类散点图")
# plt.legend()
