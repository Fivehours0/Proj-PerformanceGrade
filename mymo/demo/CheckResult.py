# -*- coding: utf-8 -*-
"""
检查处理好的 铁次化数据 各个指标 的散点分布

"""

import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 修复图片不显示中文的问题
plt.rcParams['axes.unicode_minus'] = False

path = 'data/铁次结果汇总_无滞后处理v1.0.xlsx'

df = pd.read_excel(path, index_col=0)

slag = df['铁次渣量']

intpl = slag.interpolate(method='cubic')
intpl2 = slag.interpolate(method='linear')

plt.figure()
temp1 = slag.loc[20129365:20129415]
temp1.dropna()
plt.scatter(temp1.index, temp1.values, c='b', label='origin')

temp2 = intpl.loc[20129365:20129415]
plt.plot(temp2.index, temp2.values, c='r', label='cubic')

temp3 = intpl2.loc[20129365:20129415]
plt.plot(temp3.index, temp3.values, c='g', label='linear')
plt.legend()
plt.title("插值方法比较")
plt.ylabel("铁次渣量")
plt.xlabel("铁次号")
plt.show()
# for param in range(len(df.columns)):
#     plt.figure()
#     plt.scatter(x=df.index, y=df.iloc[:, param])
#     plt.ylabel(df.columns[param])
#     plt.xlabel('铁次号')
#     plt.title(df.columns[param] + '的波动散点图')
#
#     plt.savefig('img/铁次数据散点图For异常/' + str(param) + '.png')
#     plt.show()
# plt.close()
