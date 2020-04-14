"""
高维度聚类
create time: 2020/04/13
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

if __name__ == '__main__':
    N_CLUSTERS = 5  # 聚类个数

    # 数据读入
    file = r'D:\文件\0-NEU_Works\0-攀钢项目\2-任务-铁次整理\release3.0-钢研院版本\铁次结果汇总_5h滞后v3.0.xlsx'
    input_df = pd.read_excel(file, index_col=0)

    # input_df['每小时高炉利用系数'] = 1 / input_df['每小时高炉利用系数']  # 先不进行取倒数

    # 标准化
    scaler = StandardScaler()
    scaled_np = scaler.fit_transform(input_df)
    df_scaled = pd.DataFrame(scaled_np, index=input_df.index, columns=input_df.columns)

    # 聚类

    # # 选取要被聚类特征

    X = df_scaled

    # # 聚类训练
    kmeans = KMeans(n_clusters=N_CLUSTERS)
    kmeans.fit(X)
    X['label'] = kmeans.labels_

    # 画聚类图
    plt.figure()
    for j in range(N_CLUSTERS):
        temp = X.groupby('label').get_group(j)
        plt.scatter(temp.iloc[:, 0], temp.iloc[:, 1], c=COLORS[j], label=j)

    # plt.xlabel(r'1/'+X.columns[0])
    plt.xlabel(X.columns[0])
    plt.ylabel(X.columns[1])
    plt.title(X.columns[0] + "与" + X.columns[1] + "2D聚类散点图")
    plt.legend()
    plt.savefig("C:/Users/Administrator/Desktop/figs/高维聚类.png")
    plt.show()
