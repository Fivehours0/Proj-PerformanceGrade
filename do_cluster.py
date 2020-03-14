"""
标准化处理
随机指定指标
聚类画图, 标记分类色, 2D,3D
画散点图观察
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class MyCluster:
    def __init__(self):
        # 创建类的时候就把标准化数据整理好了,不需要反复标准化
        self.df_std = self.get_standard()

    def get_standard(self):
        """
        读取整理好的每日数据 输出标准化处理后得数据
        :return:
        """
        file = './project/proj-DailyData/西昌#2高炉每日整理数据v2.2.xlsx'
        df = pd.read_excel(file)
        df['焦比'] = df['燃料比,kg/t'] - df['煤比,kg/t']
        df_std = df.copy()
        for i in range(1, df.columns.size):
            arr_std = df_std.iloc[:, i].std()
            arr_mean = df_std.iloc[:, i].mean()
            df_std.iloc[:, i] = df_std.iloc[:, i].apply(lambda x: (x - arr_mean) / arr_std)
        return df_std

    def draw_2key_cluster(self, params, n):
        """
        画2关键指标的聚类图
        :param params: ['xxx','xxx']
        :param n: 聚类个数
        :return:
        """
        colors = ['r', 'y', 'b', 'g', 'k']
        data = self.df_std.loc[:, params].dropna()

        kmeans = KMeans(n_clusters=n)
        kmeans.fit(X=data)

        data['label'] = kmeans.labels_

        plt.figure()
        for j in range(n):
            temp = data.groupby('label').get_group(j)
            plt.scatter(temp[params[0]], temp[params[1]], c=colors[j], label=j)
        plt.xlabel(params[0])
        plt.ylabel(params[1])
        plt.title("2D聚类散点图")
        plt.legend()

        plt.savefig("./img/透气性指数+焦比2D_{:d}分类图".format(n_clusters))
        plt.show()
        plt.close()
        return None


if __name__ == '__main__':
    mcs = MyCluster()
    ans = mcs.df_std
    params = ['透气性指数', '焦比']
    n_clusters = 3
    mcs.draw_2key_cluster(params, n_clusters)

