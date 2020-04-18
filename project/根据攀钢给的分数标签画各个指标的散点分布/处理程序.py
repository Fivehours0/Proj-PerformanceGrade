import pandas as pd
import os
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

PATH = 'data/铁次100plus_v3.4.xlsx'

if __name__ == '__main__':
    point_size = 10  # 点大小

    # 修改工作路径方便测试开发
    path = r"C:\Users\Administrator\Documents\GitHub\BF-grading-range\\"
    os.chdir(path)  # 也可 ../ 如此切换路径

    df = pd.read_excel(PATH, index_col=0)

    scores_low = df.where(df['现场评分'] < 75)
    scores_high = df.where(df['现场评分'] >= 75)

    dirs = 'project/根据攀钢给的分数标签画各个指标的散点分布/figs'
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    for idx in range(2, 111):
        # idx = 2
        plt.figure()
        plt.scatter(scores_low.index, scores_low.iloc[:, idx], c='b', label='小于75', s=point_size)
        plt.scatter(scores_high.index, scores_high.iloc[:, idx], c='r', label='大于等于75', s=point_size)
        plt.xlabel('铁次号')
        plt.ylabel(df.columns[idx])
        plt.legend()
        plt.savefig(dirs + "/%d.png" % idx)
        plt.show()
