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

COLORS = ['r', 'y', 'b', 'g', 'k']


class MyCluster:
    def __init__(self, params, n):
        self.params = params
        self.n = n
        # 创建类的时候就把标准化数据整理好了,不需要反复标准化
        file = 'project/proj-DailyData/西昌#2高炉每日整理数据v2.2.xlsx'
        self.df = pd.read_excel(file)
        self.df['焦比'] = self.df['燃料比,kg/t'] - self.df['煤比,kg/t']

        self.df_std = self.get_standard()
        self.df_with_label = pd.DataFrame()

    def get_standard(self):
        """
        读取整理好的每日数据 输出标准化处理后得数据
        :return:
        """

        df_std = self.df.copy()
        for i in range(1, df_std.columns.size):
            arr_std = df_std.iloc[:, i].std()
            arr_mean = df_std.iloc[:, i].mean()
            df_std.iloc[:, i] = df_std.iloc[:, i].apply(lambda x: (x - arr_mean) / arr_std)
        return df_std

    def draw_2key_cluster(self, draw=True):
        """
        画2关键指标的聚类图
        :param draw: 是否画聚类图
        :param n: 聚类个数
        :return:
        """

        data_std = self.df_std.loc[:, self.params].dropna()
        data_origin = self.df.loc[:, self.params].dropna()  # 去除缺失数据 1条
        kmeans = KMeans(n_clusters=self.n)
        kmeans.fit(X=data_std)

        data_origin['label'] = kmeans.labels_

        if draw:
            plt.figure()
            for j in range(self.n):
                temp = data_origin.groupby('label').get_group(j)
                plt.scatter(temp[self.params[0]], temp[self.params[1]], c=COLORS[j], label=j)
            plt.xlabel(self.params[0])
            plt.ylabel(self.params[1])
            plt.title("2D聚类散点图")
            plt.legend()

            plt.savefig("./img/透气性指数+焦比2D_{:d}分类图".format(self.n))
            plt.show()
            plt.close()

        self.df['label'] = data_origin['label']
        # self.df_with_label = data_origin
        return None

    def draw_other_scatter(self):
        self.draw_2key_cluster(draw=True)
        for idx in range(1, 38):  # 1~37
            plt.figure()
            for j in range(self.n):
                temp = self.df.groupby('label').get_group(j)
                x = temp.index
                y = temp.iloc[:, idx]
                plt.scatter(x, y, c=COLORS[j], label=j)
            plt.xlabel(self.df.columns[idx])
            plt.ylabel("采集项值")
            plt.title(self.df.columns[idx] + "散点图")
            plt.legend()
            plt.savefig("./img/透气性-焦比聚类后散点图/{:d}".format(idx))
            plt.show()
            plt.close()

        return None


if __name__ == '__main__':
    params = ['透气性指数', '焦比']
    n_clusters = 5

    mcs = MyCluster(params, n_clusters)
    ans = mcs.df_std
    # mcs.draw_2key_cluster()
    mcs.draw_other_scatter()
