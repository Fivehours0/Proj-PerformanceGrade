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

if __name__ == '__main__':
    N_CLUSTERS = 5  # 聚类个数
    save_fig = False
    # 数据读入
    file = r'D:\文件\0-NEU_Works\0-攀钢项目\2-任务-铁次整理\release3.0-钢研院版本\铁次结果汇总_5h滞后v3.0.xlsx'
    input_df = pd.read_excel(file, index_col=0)

    input_df['每小时高炉利用系数'] = 1 / input_df['每小时高炉利用系数']
    # 标准化
    scaler = StandardScaler()
    scaled_np = scaler.fit_transform(input_df)
    df_scaled = pd.DataFrame(scaled_np, index=input_df.index, columns=input_df.columns)

    # 聚类
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

    if save_fig:
        plt.savefig('C:/Users/Administrator/Desktop/figs/' + X.columns[0] + "与" + X.columns[1]
                    + "2D聚类散点图.png")
        plt.close()

    plt.show()

    ## 其他指标的标记效果

    df = input_df.copy()
    df['label'] = kmeans.labels_

    for index in range(39):
        plt.figure()
        for j in range(N_CLUSTERS):
            temp = df.groupby('label').get_group(j)
            plt.scatter(temp.index, temp.iloc[:, index], c=COLORS[j], label=j)

        plt.xlabel("样本序号")
        plt.ylabel(df.columns[index])
        plt.title(df.columns[index] + "分类效果图")
        plt.legend()
        if save_fig:
            plt.savefig(
                'C:/Users/Administrator/Desktop/figs/' + df.columns[index] + "分类效果图.png")
            plt.close()

        plt.show()
