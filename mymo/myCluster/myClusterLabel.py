"""
使用钢研院铁次化数据进行聚类分析
两维度 分别是 利用系数与燃料比， 聚类后 贴标签， 依旧标签分类，再观察子类常熟提取打分范围。

2020/4/11 15:00 修改
    利用系数变倒数
    画图使用标准化尺度
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

COLORS = ['r', 'y', 'b', 'g', 'k']

IMG_SAVE_PATH = '结果图/myClusterv2/'  # 结果图存放路径
N_CLUSTERS = 5  # 聚类个数
IS_SAVE_FIGURE = True # 是否保存照片

if __name__ == '__main__':
    """
    
    基于现场46个指标的新数据（铁次），使用原来的聚类方法（利用系数、燃料比）看一下是否能将不同参数的范围分开
    """


    # 数据读入
    file = r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\mymo\myCluster\铁次结果_5h滞后处理v3.0_tc.xlsx'
    input_df = pd.read_excel(file, index_col=0, sheet_name='46')

    input_df['每小时高炉利用系数'] = 1 / input_df['每小时高炉利用系数']  # 取倒数

    # 处理 数据中有 inf 的情况 去除掉
    input_df[input_df == np.inf] = np.nan
    input_df = input_df.dropna()  # 去除

    # 标准化

    scaler = StandardScaler()
    scaled_np = scaler.fit_transform(input_df)
    df_scaled = pd.DataFrame(scaled_np, index=input_df.index, columns=input_df.columns)

    # 对 1/每小时高炉利用系数 与 燃料比 进行聚类
    X = pd.DataFrame()
    X['1/每小时高炉利用系数'] = df_scaled['每小时高炉利用系数']  # 取出 利用率,燃料比
    X['燃料比'] = df_scaled['燃料比']

    kmeans = KMeans(n_clusters=N_CLUSTERS)
    kmeans.fit(X)
    X['label'] = kmeans.labels_

    # 画聚类图
    # origin = input_df.iloc[:, [0, 1]]
    # origin['label'] = kmeans.labels_
    plt.figure()
    for j in range(N_CLUSTERS):
        # temp = X.groupby('label').get_group(j)
        temp = X.groupby('label').get_group(j)
        plt.scatter(temp.iloc[:, 0], temp.iloc[:, 1], c=COLORS[j], label=j)

    plt.xlabel(X.columns[0])
    plt.ylabel(X.columns[1])
    plt.title(X.columns[0] + "与" + X.columns[1] + "2D聚类散点图")
    plt.legend()

    if IS_SAVE_FIGURE:
        plt.savefig(IMG_SAVE_PATH + X.columns[1]
                    + "2D聚类散点图.png")
        plt.close()

    plt.show()

    ## 其他指标的标记效果

    df = input_df.copy()
    df['label'] = kmeans.labels_

    for index in range(df.shape[1]-1):
        plt.figure()
        for j in range(N_CLUSTERS):
            temp = df.groupby('label').get_group(j)
            plt.scatter(temp.index, temp.iloc[:, index], c=COLORS[j], label=j)

        plt.xlabel("样本序号")
        plt.ylabel(df.columns[index])
        plt.title(df.columns[index] + "分类效果图")
        plt.legend()
        if IS_SAVE_FIGURE:
            plt.savefig(
                IMG_SAVE_PATH + str(index) + "分类效果图.png")
            plt.close()

        plt.show()
