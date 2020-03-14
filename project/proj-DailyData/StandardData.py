"""
对整理好的数据: 西昌#2高炉每日整理数据v2.2.xlsx 进行正态标准化

再进行 聚类聚类处理
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
        self.df_std = pd.DataFrame()
        self.df_std = self.get_standard()

    def get_standard(self, out_xlxs: bool = False) -> pd.DataFrame:
        """
        读取整理好的每日数据 输出标准化处理后得数据
        :param: out_xlxs 是否输出为 xlsx 文件
        :return:
        """
        std = StandardScaler()

        file = '西昌#2高炉每日整理数据v2.2.xlsx'
        df = pd.read_excel(file)

        df_std = df.copy()
        for i in range(1, df.columns.size):
            # df_std.iloc[:,i] = std.fit_transform(df_std.iloc[:,i:i+1].values) # fit_transfrom 不支持处理有NaN的数据
            arrStd = df_std.iloc[:, i].std()
            arrMean = df_std.iloc[:, i].mean()
            df_std.iloc[:, i] = df_std.iloc[:, i].apply(lambda x: (x - arrMean) / arrStd)
        if out_xlxs:
            df_std.to_excel("./project/proj-DailyData/西昌#2高炉每日整理数据v2.2_标准化.xlsx")  # 输出文件

        return df_std

    def draw3Dcluster(self, index: int = 3, n: int = 3, azim=-60, elev=30) -> None:
        """
        画3D聚类图
        :param index: 选取得第三指标 取值范围 3~36
        :param n: 聚类数 建议取值 3 or 5
        :param elev: 改变绘制图像的视角,即相机的位置,azim沿着z轴旋转，elev沿着y轴
        :param azim: 改变绘制图像的视角,即相机的位置,azim沿着z轴旋转，elev沿着y轴
        :return:
        """
        df_std = self.df_std
        # i = 4 # 3 到 36
        X = df_std.iloc[:, [1, 2, index]].dropna()

        # # 聚类
        # n = 3
        kmeans = KMeans(n_clusters=n)
        kmeans.fit(X)
        X['label'] = kmeans.labels_

        colors = ['r', 'y', 'b', 'g', 'k']
        # 教程来自: https://blog.csdn.net/weixin_41297324/article/details/83856832
        ax = plt.figure().add_subplot(111, projection='3d')
        for j in range(n):
            temp = X.groupby('label').get_group(j)
            ax.scatter(temp.iloc[:, 0], temp.iloc[:, 1], temp.iloc[:, 2], c=colors[j], label=str(j), marker='^')
        # ax.scatter(X.iloc[:, 0], X.iloc[:, 1], X.iloc[:, 2], c=X.iloc[:, 3], label=X.iloc[:, 3], marker='^') # 一次性画 无法添加 legend
        ax.view_init(elev=elev, azim=azim) # learn from https://blog.csdn.net/noah_cyz/article/details/79125640?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task
        ax.set_xlabel(X.columns[0])
        ax.set_ylabel(X.columns[1])
        ax.set_zlabel(X.columns[2])
        ax.set_title(df_std.columns[index] + "三维聚类图")
        ax.legend()

    def draw2Dcluster(self, index: int, n: int = 3, alpha: float = 0.5) -> None:
        """
        画2D混合 聚类图
        :param index: 同3D
        :param n: 同3D
        :param alpha: 日产量与燃料比得加权系数: alpha * 日产量 + (1-alpha) * 燃料比
        :return: None
        """
        df_std = self.df_std

        X = df_std.iloc[:, [1, 2, index]].dropna()
        name = df_std.columns[index]
        X['混合'] = alpha * X.iloc[:, 0] + (1 - alpha) * X.iloc[:, 1]
        kmeans = KMeans(n_clusters=n)
        kmeans.fit(X.loc[:, ['混合', name]])
        X['label'] = kmeans.labels_

        colors = ['r', 'y', 'b', 'g', 'k']
        plt.figure()
        for j in range(n):
            temp = X.groupby('label').get_group(j)
            plt.scatter(temp['混合'], temp[name], c=colors[j], label=j)

        plt.xlabel("{:.2f}*日产量+{:.2f}*燃料比".format(alpha, 1 - alpha))
        plt.ylabel(name)
        plt.title(name + "2D聚类散点图")
        plt.legend()


if __name__ == '__main__':
    mc = MyCluster()

    # 3D
    i = 5  # i 取值范围3到36
    n = 3  # 聚几类? # 取值3-5
    for i in range(3,37):
        mc.draw3Dcluster(i, n,azim=-120)
        plt.savefig("./img/3D/" + str(i)+'_1')
        plt.close()

        mc.draw3Dcluster(i, n,azim=-60)
        plt.savefig("./img/3D/" + str(i)+'_2')
        plt.close()

        mc.draw3Dcluster(i, n,azim=0)
        plt.savefig("./img/3D/" + str(i)+'_3')
        plt.close()

    # for i in range(3,37):
    #     mc.draw2Dcluster(i, n)
    #     plt.savefig("./img/2D"+str(i))
    #     plt.close()
