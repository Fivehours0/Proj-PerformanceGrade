# -*- coding: utf-8 -*-
"""
检查处理好的 铁次化数据 各个指标 的散点分布

"""

import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 修复图片不显示中文的问题
plt.rcParams['axes.unicode_minus'] = False

path = 'data/铁次结果_无滞后处理.xlsx'

df = pd.read_excel(path, index_col=0)

for param in range(len(df.columns)):
    plt.figure()
    plt.scatter(x=df.index, y=df.iloc[:, param])
    plt.ylabel(df.columns[param])
    plt.xlabel('铁次号')
    plt.title(df.columns[param] + '的波动散点图')

    plt.savefig('img/铁次数据散点图For异常/' + str(param) + '.png')
    plt.show()
    # plt.close()
