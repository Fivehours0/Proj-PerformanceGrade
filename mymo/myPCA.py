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


def pca_iron_order(input_df, n_components):
    # 标准化
    scaler = StandardScaler()
    scaled_np = scaler.fit_transform(input_df)
    df_scaled = pd.DataFrame(scaled_np, index=input_df.index, columns=input_df.columns)

    # PCA
    n = n_components
    pca = PCA(n)
    pca.fit(scaled_np)
    pca.explained_variance_ratio_.cumsum()
    df_pca = pca.transform(scaled_np)

    # 打分图
    score = df_pca.dot(pca.explained_variance_.reshape(n, 1)) / pca.explained_variance_.sum()
    plt.scatter(range(0, 100), score[:100], label='PCA', c='r')
    plt.plot(range(0, 100), df_scaled['铁次铁量'].iloc[:100], label='铁次铁量', c='b')
    plt.plot(range(0, 100), df_scaled['燃料比'].iloc[:100], label='燃料比', c='g')
    plt.legend()
    plt.show()

    # 打分成绩和各个指标的相关性
    df_scaled['score'] = score
    df_corr = df_scaled.corr()
    res_corr = df_corr.sort_values('score')['score']
    return res_corr, pca


if __name__ == '__main__':
    # 铁次的
    file = r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\铁次结果汇总_5h滞后处理v2.0.xlsx'
    df = pd.read_excel(file, index_col=0)
    res_corr, pca = pca_iron_order(df, 30)

    # # 把每日版数据读入进来
    # file = r"C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\西昌#2高炉每日整理数据v2.2.xlsx"
    # df = pd.read_excel(file, index_col=0)
    # only2019 = True
    # if only2019:
    #     df = df[df.index >= pd.to_datetime('2019-01-01 00:00:00')]
    # # 去除缺失太多的 指标(共计418, 这个缺的仅仅有150左右的有效值)
    # # '风量,m3/min', '实际风速,m/s' 相关性较高 去除
    # params_too_less = ['[C],%', 'δ[Ti]', 'δR2', '炉身下二层温度极差,℃', 'M10,%', 'CRI,%', '风量,m3/min', '实际风速,m/s']
    # df.drop(columns=params_too_less, inplace=True)
    # df.fillna(df.mean(), inplace=True)  # 使用均值填充缺失值
    # df.rename(columns={'日产量,t/d': '铁次铁量', '燃料比,kg/t': '燃料比'}, inplace=True)
    # res2 = pca_iron_order(df, n_components=13)

    # # 输出pca_component表
    index_name = ["主成分%d" % i for i in range(1, 30 + 1)]
    pca_component = pd.DataFrame(pca.components_, index=index_name, columns=df.columns)
    # pca_component.to_excel('pca_component.xlsx')
    data = pca.explained_variance_ratio_.reshape(1, 30).dot(pca.components_)
    score_weight = pd.DataFrame(data.T, index=df.columns)
