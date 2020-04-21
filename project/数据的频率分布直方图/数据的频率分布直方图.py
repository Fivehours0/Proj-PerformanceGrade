import pandas as pd
import os
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
COLORS = ['r', 'g', 'b']
PATH = 'data/铁次100plus_v3.4.xlsx'


def draw_pic(idx):
    """
    绘制图, 这是一个inline 函数 会从被调用处读取外部变量
    :return:
    """
    x1, x2, x3 = bad.iloc[:, idx], middle.iloc[:, idx], good.iloc[:, idx]  # 优 中 差

    param_name = df.columns[idx]  # 参数名

    plt.figure()
    # 画分布直方图
    plt.subplot(2, 1, 1)
    kwargs = dict(alpha=0.3, bins=30, density=True)
    plt.hist(x1, color=COLORS[0], label='0~75', **kwargs)
    plt.hist(x2, color=COLORS[1], label='75~85', **kwargs)
    plt.hist(x3, color=COLORS[2], label='85~100', **kwargs)
    plt.xlabel(param_name)
    plt.ylabel('分布频率')
    plt.legend()

    plt.subplot(2, 1, 2)

    # 画散点图
    kwargs = dict(s=8, alpha=0.3)
    plt.scatter(x1, bad.index, c=COLORS[0], label='0~75', **kwargs)
    plt.scatter(x2, middle.index, c=COLORS[1], label='75~85', **kwargs)
    plt.scatter(x3, good.index, c=COLORS[2], label='85~100', **kwargs)

    # 画均值线
    kwargs = dict(ymin=iron_min, ymax=iron_max)
    plt.vlines(x1.mean(), color=COLORS[0], **kwargs)
    plt.vlines(x2.mean(), color=COLORS[1], **kwargs)
    plt.vlines(x3.mean(), color=COLORS[2], **kwargs)

    plt.xlabel(param_name)
    plt.ylabel('铁次号')
    plt.legend()

    plt.savefig(save_path + "%d.png" % idx)
    plt.close()
    plt.show()


if __name__ == '__main__':
    # 修改工作路径方便测试开发
    path = "../../"
    os.chdir(path)  # 也可 ../ 如此切换路径
    print(os.getcwd())

    # load data
    df = pd.read_excel(PATH, index_col=0)

    # 筛选数据
    bad = df.where(df['现场评分'] < 75).dropna(how='all')
    good = df.where(df['现场评分'] >= 85).dropna(how='all')
    middle = df.where((75 <= df['现场评分']) & (df['现场评分'] < 85)).dropna(how='all')

    # 画均值竖线的准备
    iron_min = df.index.min()
    iron_max = df.index.max()

    # 保存路径设定
    save_path = 'project/数据的频率分布直方图/figs/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #
    for i in range(2, 114 - 3):
        draw_pic(i)
