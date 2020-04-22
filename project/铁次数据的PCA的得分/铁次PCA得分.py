"""
PCA的分计算
沿袭 mymo.myPCA
"""
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 常量设定区
FILE = 'data/铁次100plus_v3.4.xlsx'  # 数据路径

OUT_PATH = 'project/铁次数据的PCA的得分/'
if __name__ == '__main__':
    os.chdir('../../')
    print("当前工作路径：%s" % os.getcwd())

    # load data
    df = pd.read_excel(FILE, index_col=0)
    df = df.iloc[:, 2:111]  # 摘除得分和受铁开始与结束时间

    # 标准化
    scaler = StandardScaler()
    scaled_np = scaler.fit_transform(df)
    df_scaled = pd.DataFrame(scaled_np, index=df.index, columns=df.columns)  # 标准化的数据

    # PCA

    # 主成分个数暂时取None
    pca = PCA(None)
    pca.fit(scaled_np)  # 训练
    t = pca.explained_variance_ratio_.cumsum()  # 累计值建议取值 0.9 0.95
    first_bigger_threshold = np.where(t > 0.9)[0][0]  # 第一个累计解释量大于阈值的下标
    print("主成分个数取%d时,解释总和大于90%%" % (first_bigger_threshold + 1))

    # 根据阈值确定好主成分个数 重新计算PCA
    N_COMPONENTS = first_bigger_threshold + 1
    pca = PCA(N_COMPONENTS)
    pca.fit(scaled_np)  # 训练
    df_pca = pca.transform(scaled_np)  # 每条样本在各个主成分上的得分

    # 计算PCA的得分
    score = df_pca.dot(pca.explained_variance_.reshape(N_COMPONENTS, 1)) / pca.explained_variance_.sum()
    score = -1 * score
    # 绘制打分图
    plt.figure()
    plt.plot(range(score.shape[0]), score)
    plt.show()

    # 绘制PCA的得分的直方图
    plt.figure()
    bins = 35
    a = plt.hist(x=score, bins=bins, normed=True)
    plt.ylabel('分布频率')
    plt.xlabel('PCA得分')
    plt.title('PCA的得分的频率分布直方图(bin=%d)' % bins)
    plt.show()

    threshold_classify_point = (a[1][22] + a[1][23]) / 2  # 观察图 确定 低 22 - 23 个bin 是阈值发生的地方

    # 根据阈值分好样本 差样本
    df['pca_score'] = score

    df_good = df.where(df['pca_score'] >= threshold_classify_point).dropna()
    df_bad = df.where(df['pca_score'] < threshold_classify_point).dropna()

    df_good.to_excel(OUT_PATH + '铁次100plus_v3.4_pca_good.xlsx')
    df_bad.to_excel(OUT_PATH + '铁次100plus_v3.4_pca_bad.xlsx')
