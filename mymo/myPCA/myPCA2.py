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
    """
    2020-4-17指导：
     基于现场46个指标的新数据（铁次），基于PCA的分值看一下规律
    """
    FILE = '铁次结果_5h滞后处理v3.0_tc.xlsx'
    N_COMPONENTS = 21  # 主成分个数, 需要先设定 None

    # 数据读入
    input_df = pd.read_excel(FILE, index_col=0, sheet_name='46')

    # 标准化
    scaler = StandardScaler()
    scaled_np = scaler.fit_transform(input_df)
    df_scaled = pd.DataFrame(scaled_np, index=input_df.index, columns=input_df.columns)

    # PCA
    n = N_COMPONENTS
    pca = PCA(n)
    pca.fit(scaled_np)
    pca.explained_variance_ratio_.cumsum()  # 累计值去 0.9 0.95
    df_pca = pca.transform(scaled_np)

    # 打分图
    score = df_pca.dot(pca.explained_variance_.reshape(n, 1)) / pca.explained_variance_.sum()
    max_range = score.shape[0]
    plt.scatter(range(0, max_range), score[:max_range], label='PCA', c='r')
    plt.plot(range(0, max_range), df_scaled['每小时高炉利用系数'].iloc[:max_range], label='每小时高炉利用系数', c='b')
    plt.plot(range(0, max_range), df_scaled['燃料比'].iloc[:max_range], label='燃料比', c='g')
    plt.legend()
    plt.show()  # 太密集了

    # 部分图
    min_range = 100
    max_range = 200
    plt.scatter(range(min_range, max_range), score[min_range:max_range], label='PCA', c='r')
    plt.plot(range(min_range, max_range), df_scaled['每小时高炉利用系数'].iloc[min_range:max_range], label='每小时高炉利用系数', c='b')
    plt.plot(range(min_range, max_range), df_scaled['燃料比'].iloc[min_range:max_range], label='燃料比', c='g')
    plt.title('部分样本的PCA得分与利用系数,燃料比关系图')
    plt.legend()
    plt.show()

    # PCA打分成绩和各个指标的相关性
    df_scaled['score'] = score
    df_corr = df_scaled.corr()
    res_corr = df_corr.sort_values('score')['score']

    plt.savefig('C:/Users/Administrator/Desktop/pca图.png')