import os
import pandas as pd
import numpy as np

"""
合并所有批次数据
"""
PATHS = [
    r'organize/cache/铁次5h滞后_19.xlsx',
    r'organize/cache/铁次5h滞后_20.xlsx',
    r'organize/cache/铁次5h滞后_201.xlsx',
    r'organize/cache/铁次5h滞后_all.xlsx',
    r'organize/cache/铁次5h滞后_缺失填充处理后.xlsx'
]
if __name__ == '__main__':
    # fix work path
    os.chdir('../')
    print(os.getcwd())

    df19 = pd.read_excel(PATHS[0], index_col=0)  # 117
    df20 = pd.read_excel(PATHS[1], index_col=0)  # 118
    df201 = pd.read_excel(PATHS[2], index_col=0)  # 118

    # 手动检查一下是不是所有的表的指标是不是一样多

    dfz = pd.concat([df19, df20, df201])  # 2278, 118

    dfz.to_excel(PATHS[3])

    temp = dfz
    # 去除 缺失程度超过 2成的 采集项指标
    list_lack = list(temp.columns[temp.count() / temp.shape[0] < 0.8])
    print("去除 缺失程度超过 2成的 采集项指标: ")
    print(list_lack)
    droped = temp.drop(columns=list_lack)

    # 去除 缺失程度超过 2成的 样本
    list_lack = list(droped.index[droped.count(axis=1) / droped.shape[1] < 0.8])
    print("去除 缺失程度超过 2成的 样本")
    print(list_lack)
    droped2 = droped.drop(index=list_lack)

    droped3 = droped2.replace(np.inf)  # 去除inf
    droped3 = droped3.ffill().bfill()  # 前向后向填充
    droped3.to_excel(PATHS[4])

    # 注意去除 铁次小于20128461的数据
