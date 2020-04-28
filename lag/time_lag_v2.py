# -*- coding: UTF-8 -*-
"""
应对任务4进行的开发

计划实现数据处理与滞后分析的分类

"""
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def lag_analysis(i, j, lag_min, lag_max, res, img_show=False, draw_range='small'):
    """
    i: 控制参数的序号
    j: 生产参数的序号
    lag_min: 最小滞后时间
    lag_max: 最大滞后时间
    res: 数据表
    img_show: 是否展示图像, 默认False
    draw_range: 默认 'small'(画前两天的图); 'big': 传入数据中的所有区间的图
    """
    # 画图得开始与结束时间 设定:

    if draw_range == 'big':
        draw_start, draw_end = res.index[0], res.index[-1]  # 传入数据中的所有区间的图
    else:
        draw_start, draw_end = res.index[0], res.index[0] + pd.to_timedelta('2d')  # 画前两天的图

    ctrl = res[controls[i]]
    prod = res[products[j]]

    # 绘制没有进行滞后处理的散点连线图
    plt.figure()
    ctrl_std = (ctrl - ctrl.mean()) / ctrl.std()  # 正态标准化
    ctrl_std[draw_start:draw_end].plot(label=controls[i])
    prod_std = (prod - prod.mean()) / prod.std()
    prod_std[draw_start:draw_end].plot(label=products[j])
    plt.title("{}与{}的波动图(未滞后处理)".format(products[j], controls[i]))
    plt.ylabel("正态标准化数值")
    plt.legend()

    plt.savefig(FIG_SAVE_PATH + "{}与{}的波动图(未滞后处理)".format(products[j], controls[i]))
    if img_show:
        plt.show()
    else:
        plt.close()

    #  滞后分析部分
    corr_list = []
    for periods in range(lag_min * 60, lag_max * 60 + 1):
        corr_list.append(ctrl.shift(periods).corr(prod))

    # 滞后分析图
    plt.figure()
    plt.plot(range(lag_min * 60, lag_max * 60 + 1), np.abs(corr_list))
    plt.xlabel("滞后时间/min")
    plt.ylabel("绝对相关系数")
    np_corr_list = np.abs(np.array(corr_list))

    max_corr_value_id = np_corr_list.argmax()  # 相关系数绝对值的最大值
    max_corr_value = np_corr_list.max()
    lag_time = max_corr_value_id + lag_min * 60
    plt.scatter(lag_time, max_corr_value, c='r')

    plt.title("{}与{}的滞后时间分析图(滞后结果:{}min)".format(products[j], controls[i], lag_time))

    print("{}与{}的滞后时间分析图(滞后结果:{}min)".format(products[j], controls[i], lag_time))

    plt.savefig(FIG_SAVE_PATH + "{}与{}的滞后时间分析图".format(products[j], controls[i], lag_time))
    if img_show:
        plt.show()
    else:
        plt.close()

    # 滞后处理后的图
    fig_name3 = "{}与{}的波动图(滞后处理后)".format(products[j], controls[i])
    plt.figure()
    ctrl_std[draw_start:draw_end].shift(lag_time).plot(label=controls[i])
    prod_std[draw_start:draw_end].plot(label=products[j])
    plt.title(fig_name3)
    plt.ylabel("正态标准化数值")

    plt.legend()
    plt.savefig(FIG_SAVE_PATH + fig_name3)
    if img_show:
        plt.show()
    else:
        plt.close()
    return lag_time, max_corr_value  # 输出滞后时间与最大绝对相关系数


def chdir():
    """
    修改工作路径
    :return:
    """
    os.chdir('../')
    print('当前时滞分析的程序的工作路径：', os.getcwd())


if __name__ == '__main__':
    chdir()

    date_start = '2020-1-5'
    date_end = '2020-1-15'

    # 读取已经整理好的分钟数据 选取适合的时间段
    res = pd.read_excel('lag/时滞分析的分钟数据.xlsx')

    bools = (pd.to_datetime(date_start) < res['业务处理时间']) & (res['业务处理时间'] < pd.to_datetime(date_end))
    selected = res.where(bools).dropna()
    res = selected
    res.set_index('业务处理时间', inplace=True)

    # read config
    config = pd.read_excel('lag/lag_config.xlsx', index_col=0, header=[0, 1])  # lag_config.lagfig 其实是CSV 文件

    controls = config.index
    products = [i[0] for i in config.columns][::2]

    # 存储路径
    FIG_SAVE_PATH = 'lag/figs/'
    if not os.path.exists(FIG_SAVE_PATH):
        os.makedirs(FIG_SAVE_PATH)

    lag_res_table = pd.DataFrame(data=0, index=controls, columns=products)  # 滞后时间的结果存放表
    corr_value_table = pd.DataFrame(data=0, index=controls, columns=products)  # 最大相关系数的结果存放表
    big_scale_params = ['焦炭负荷', '铁水温度', '球团矿比例']  # 对于'焦炭负荷','[铁水温度]'等 这样的指标 要画大尺度时间的散点波动图
    for j in range(len(products)):

        for i in range(len(controls)):
            lag_min = config.loc[controls[i], (products[j], 'min')]  # 时滞时间的最小值
            lag_max = config.loc[controls[i], (products[j], 'max')]  # 最大值
            if products[j] in big_scale_params or controls[i] in big_scale_params:
                lag_res_table.loc[controls[i], products[j]], corr_value_table.loc[
                    controls[i], products[j]] = lag_analysis(i, j, lag_min, lag_max, res, draw_range='big')
            else:
                lag_res_table.loc[controls[i], products[j]], corr_value_table.loc[
                    controls[i], products[j]] = lag_analysis(i, j, lag_min, lag_max, res)

    # save table to excel
    lag_res_table.to_excel('lag/滞后结果表.xlsx')
    corr_value_table.to_excel('lag/最大相关系数.xlsx')
