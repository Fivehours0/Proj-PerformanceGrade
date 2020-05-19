# -*- coding: UTF-8 -*-

import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

if __name__ == '__main__':
    df = pd.read_excel(
        r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\西昌2#高炉现场数据_2019年至今 - 钢研院打分数据\自整理.xlsx',
        index_col=0, header=[0, 1])
    # 存储路径
    FIG_SAVE_PATH = 'figs-pan-daily/'
    if not os.path.exists(FIG_SAVE_PATH):
        os.makedirs(FIG_SAVE_PATH)
    for i in range(34):
        plt.figure()
        df.iloc[:, i].plot()
        plt.title(df.columns[i])
        plt.savefig(FIG_SAVE_PATH + str(i))
        plt.show()
