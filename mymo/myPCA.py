"""
复现文献：
“基于主成分分析的高炉指标评价方法_曹维超”
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

if __name__ == '__main__':
    # 把每日版数据读入进来
    file = r"C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\西昌#2高炉每日整理数据v2.2.xlsx"
    df = pd.read_excel(file, index_col=0)

    # 去除缺失太多的 指标(共计418, 这个缺的仅仅有150左右的有效值)
    # '风量,m3/min', '实际风速,m/s' 相关性较高 去除
    params_too_less = ['[C],%', 'δ[Ti]', 'δR2', '炉身下二层温度极差,℃', 'M10,%', 'CRI,%', '风量,m3/min', '实际风速,m/s']
    df.drop(columns=params_too_less, inplace=True)

    df.fillna(df.mean(), inplace=True)  # 使用均值填充缺失值

    # 标准化
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)
    DF_scaled = pd.DataFrame(df_scaled, index=df.index, columns=df.columns)

    # PCA
    pca = PCA(17)
    pca.fit(df_scaled)
    df_pca = pca.transform(df_scaled)

    # 输出pca_component表
    index_name = ["主成分%d" % i for i in range(1, 18)]
    columns_name = df.columns
    pca_component = pd.DataFrame(pca.components_, index=index_name, columns=df.columns)
    pca_component.to_excel('pca_component.xlsx')

    # 打分图
    score = df_pca.dot(pca.explained_variance_.reshape(17, 1)) / pca.explained_variance_.sum()
    plt.scatter(range(418), score, label='PCA', c='r')
    plt.plot(range(418), DF_scaled['日产量,t/d'], label='日产量', c='b')
    plt.plot(range(418), DF_scaled['燃料比,kg/t'], label='燃料比', c='g')
    plt.plot(range(418), DF_scaled['煤比,kg/t'], label='煤比', c='y')
    plt.legend()
    plt.show()

    # 打分成绩和各个指标的相关性
    # DF_scaled['score'] = score
    # Corr = DF_scaled.corr()
    # Corr.sort_values('score')['score']

    rank = DF_scaled.rank()
    rank[rank['score'] < 83].mean() / 417
