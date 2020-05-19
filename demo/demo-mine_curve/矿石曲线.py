# -*- coding: UTF-8 -*-
"""
画矿石波动曲线 看一看这三批数据（2019-11月到2020-3月）是不是同一料批

"""
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

if __name__ == '__main__':
    df = pd.read_excel(r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\organize2\铁次5h滞后_缺失填充处理后.xlsx',
                       index_col=0)

    # 存储路径
    FIG_SAVE_PATH = 'figs/'
    if not os.path.exists(FIG_SAVE_PATH):
        os.makedirs(FIG_SAVE_PATH)
    for i in range(10):
        plt.figure()
        df.iloc[:, i].plot()
        plt.title(df.columns[i])
        plt.savefig('figs/'+str(i))
        plt.show()
