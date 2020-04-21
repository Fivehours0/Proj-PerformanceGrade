"""
使用钢研院铁次化数据进行聚类分析
聚类的两个维度分别是 利用系数与燃料比的混合指标 + 第三维度
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

def draw_2d_cluster(index):
    """
    画二维聚类
    :param index: 第三指标
    :return:
    """
    n_clusters = N_CLUSTERS
    # index = 2  # 第三指标
    X = df_scaled.iloc[:, [0, 1, index]]  # 取出 利用率,燃料比,第三指标
    name = df_scaled.columns[index]
    X['混合'] = ALPHA * X.iloc[:, 0] + (1 - ALPHA) * X.iloc[:, 1] * -1
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X.loc[:, ['混合', name]])

    X['label'] = kmeans.labels_

    # ## 第三指标的尺度是标准化的
    # plt.figure()
    # for j in range(n):
    #     temp = X.groupby('label').get_group(j)
    #     plt.scatter(temp['混合'], temp[name], c=COLORS[j], label=j)
    #
    # plt.xlabel("{:.2f}*日产量+{:.2f}*燃料比*(-1)".format(ALPHA, 1 - ALPHA))
    # plt.ylabel(name)
    # plt.title(name + "2D聚类散点图")
    # plt.legend()
    # plt.show()

    origin = input_df.iloc[:, [0, 1, index]]
    origin['label'] = kmeans.labels_
    plt.figure()
    for j in range(n_clusters):
        temp = X.groupby('label').get_group(j)
        temp2 = origin.groupby('label').get_group(j)
        plt.scatter(temp['混合'], temp2[name], c=COLORS[j], label=j)

    plt.xlabel("{:.2f}*日产量+{:.2f}*燃料比*(-1)".format(ALPHA, 1 - ALPHA))
    plt.ylabel(name)
    plt.title(name + "2D聚类散点图")
    plt.legend()

    plt.savefig(IMG_SAVE_PATH + str(index) + "2D聚类散点图.png")
    plt.close()

    plt.show()


if __name__ == '__main__':
    N_CLUSTERS = 5  # 聚类个数
    ALPHA = 0.6  # 指标混合系数

    # 数据读入

    file = r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\mymo\myCluster\铁次结果_5h滞后处理v3.0_tc.xlsx'
    input_df = pd.read_excel(file, index_col=0, sheet_name='46')

    # 处理 数据中有 inf 的情况 去除掉
    input_df[input_df == np.inf] = np.nan
    input_df = input_df.dropna()  # 去除

    # 标准化
    scaler = StandardScaler()
    scaled_np = scaler.fit_transform(input_df)
    df_scaled = pd.DataFrame(scaled_np, index=input_df.index, columns=input_df.columns)

    for i in range(3, df_scaled.shape[1]):
        draw_2d_cluster(i)
