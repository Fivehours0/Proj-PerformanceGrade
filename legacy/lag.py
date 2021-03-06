"""
3月22日前搞出 滞后时间
画参数的曲线
画滞后取值曲线

时间滞后分析v5.0
计算控制参数与生产指标之间的时间滞后
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from mymo.get_things import get_df
from mymo.get_things import get_time_table

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def process_time_data(params):
    """
    数据必须 有 有效的!! 业务处理时间!!
    
    收入指标名称 输出 整理好的一分钟频率采集的数据表
    
    在同一个pkl文件的处理
    
    """
    res = pd.DataFrame()

    # 19 20 年的数据都读取进来
    df19 = get_df(params[0], 19)
    df20 = get_df(params[0], 20)
    df = pd.concat([df19, df20])

    df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])  # 格式化
    df['采集项值'][df['采集项值'] > 1e7] = None  # 去除 99999
    for param in params:
        grouped = df.groupby('采集项名称').get_group(param)
        grouped = grouped.set_index('业务处理时间')
        resampled = grouped.resample('1T').agg(np.mean).rename(columns={'采集项值': param})  # 重采样1min
        temp = resampled.interpolate()  # 线性插值
        res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)
    return res


def process_iron_order_data(params):
    """
    处理铁次号型的数据.
    把受铁开始时间当业务处理时间
    之间的间隙使用线性插值填充
    """
    res = pd.DataFrame()
    df_iorn_time = pd.concat([get_time_table(19), get_time_table(20)])

    df = pd.concat([get_df(params[0], 19), get_df(params[0], 20)])
    df['铁次号'] = pd.to_numeric(df['铁次号'])
    df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化
    df = df[df['铁次号'] >= 20000000]  # 提取出#2高炉的数据
    df = df[df['铁次号'] < 30000000]

    for param in params:
        # param = params[0]
        grouped = df.groupby("采集项名称").get_group(param)
        grouped = grouped.groupby("铁次号").mean()
        # grouped_idx = grouped.set_index('铁次号').sort_index()
        merged = pd.merge(df_iorn_time['受铁开始时间'], grouped, how='outer', left_index=True,
                          right_index=True)
        merged = merged.rename(columns={'受铁开始时间': '业务处理时间'}).set_index('业务处理时间')
        resampled = merged.resample('1T').agg(np.mean).rename(columns={'采集项值': param})  # 重采样1min
        temp = resampled.interpolate()  # 线性插值
        res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)
    # temp=process_time_data(params)
    return res


def get_datas():
    ## 测试代码: 查验各个指标是在哪个表里 集中处理更有效率
    # param_list = "热风温度 送风风量 热风压力 富氧量\
    #               焦炭负荷 炉顶压力1 炉顶压力2\
    #               炉腹煤气发生量  炉顶温度1  炉喉温度1 炉顶煤气CO  炉顶煤气CO2  \
    #               喷吹速率 \
    #               理论燃烧温度 鼓风动能\
    #               [铁水温度] \
    #               [Si] [Ti] [S] \
    #               (CaO) (SiO2)   ".split()
    #
    # for item in param_list:
    #     print(find_table(item, 19))

    res = pd.DataFrame()
    ####################################################################################################################
    # 热风温度 送风风量 热风压力 富氧量
    params = "热风温度 送风风量 热风压力 富氧量 ".split()
    temp = process_time_data(params)
    res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)
    ####################################################################################################################
    # 焦炭负荷 炉顶压力
    params = "焦炭负荷 炉顶压力1 炉顶压力2 ".split()
    temp = process_time_data(params)
    res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)
    luding_mean = res[['炉顶压力1', '炉顶压力2']].mean(axis=1)
    #  透气性指数 = 送风风量/(热风压力-炉顶压力1-2) *100
    res['透气性指数'] = res['送风风量'] / (res['热风压力'] - luding_mean) * 100
    ####################################################################################################################
    # 炉腹煤气发生量  炉顶温度  炉喉温度 煤气利用率 #
    params = "炉腹煤气发生量  炉顶温度1  炉喉温度1 炉顶煤气CO  炉顶煤气CO2 \
        炉顶温度2 炉顶温度3 炉顶温度4 炉喉温度2 炉喉温度3 炉喉温度4 炉喉温度5\
        炉喉温度6 炉喉温度7 炉喉温度8".split()
    temp = process_time_data(params)
    res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)

    res['煤气利用率'] = res['炉顶煤气CO2'] / (res['炉顶煤气CO'] + res['炉顶煤气CO2'])
    res['炉顶温度(极差)'] = (res[['炉顶温度1', '炉顶温度2', '炉顶温度3', '炉顶温度4']].max(axis=1)
                       - res[['炉顶温度1', '炉顶温度2', '炉顶温度3', '炉顶温度4']].min(axis=1))
    res['炉喉温度(极差)'] = (res[['炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6', '炉喉温度7', '炉喉温度8']].max(axis=1)
                       - res[['炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6', '炉喉温度7', '炉喉温度8']].min(axis=1))
    ####################################################################################################################
    # 理论燃烧温度 鼓风动能 #
    ####################
    params = "理论燃烧温度 鼓风动能".split()
    temp = process_time_data(params)
    res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)

    ####################################################################################################################
    # 计算喷吹速率 #
    temp = process_time_data(['喷吹速率'])
    res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)

    ####################################################################################################################
    # 计算[Si] [Ti] [S] #
    params = "[Si] [Ti] [S]".split()
    temp = process_iron_order_data(params)
    res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)
    res['[Si]+[Ti]'] = res['[Si]'] + res['[Ti]']

    res['[铁水温度]'] = process_iron_order_data(['[铁水温度]'])

    ####################################################################################################################
    # 计算R2 #
    params = "(CaO) (SiO2)".split()
    temp = process_iron_order_data(params)
    res = pd.merge(res, temp, how="outer", left_index=True, right_index=True)
    res['R2'] = res['(CaO)'] / res['(SiO2)']

    ####################################################################################################################
    # 计算矿石比例 #
    """
    对各个矿石每隔2小时做累加, 并且 这两个小时的所有分钟时刻 都是这个矿石比例
    处理前:
                             矿A     矿B
    2020-01-01 00:01:00       1       4
    2020-01-01 00:02:00       2       8
    2020-01-01 00:03:00       3       2
    2020-01-01 00:04:00       4       6
    
    处理后:
                             矿A     矿B
    2020-01-01 00:01:00      0.2     0.8
    2020-01-01 00:02:00      0.2     0.8
    2020-01-01 00:03:00      0.47    0.53
    2020-01-01 00:04:00      0.47    0.53
     
    
    """
    # param_list = "40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()
    param_list = "40赤块 南非块矿 烧结矿 酸性烧结矿 白马球团".split()
    # temp = process_time_data(param_list)
    # param = param_list[0]

    df19 = get_df(param_list[0], 19)
    df20 = get_df(param_list[0], 20)
    df = pd.concat([df19, df20])

    df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])  # 格式化
    df['采集项值'][df['采集项值'] > 1e7] = None  # 去除 99999
    res_tmp = pd.DataFrame()
    for param in param_list:
        grouped = df.groupby('采集项名称').get_group(param)
        grouped = grouped.set_index('业务处理时间')
        resampled = grouped.resample('2h').agg(np.sum).rename(columns={'采集项值': param})  # 重采样1min
        res_tmp = pd.merge(res_tmp, resampled, how="outer", left_index=True, right_index=True)
    res_tmp['块矿比例'] = res_tmp['40赤块'] + res_tmp['南非块矿']
    res_tmp['烧结比例'] = res_tmp['烧结矿'] + res_tmp['酸性烧结矿']
    res_tmp['球团比例'] = res_tmp['白马球团']
    res_tmp = res_tmp.loc[:, ['块矿比例', '烧结比例', '球团比例']]
    # 计算比例
    res_sum = res_tmp.sum(axis=1)
    for param in ['块矿比例', '烧结比例', '球团比例']:
        res_tmp[param] = res_tmp[param] / res_sum
    res = pd.merge(res, res_tmp, how="outer", left_index=True, right_index=True)

    # nan值填充
    for param in ['块矿比例', '烧结比例', '球团比例']:
        # res[param] = res[param].ffill()
        res[param] = res[param].interpolate(method='quadratic')
    return res


def lag_analysis(i, j, lag_min, lag_max, img_show=False, draw_range='small'):
    """
    i: 控制参数的序号
    j: 生产参数的序号
    lag_min: 最小滞后时间
    lag_max: 最大滞后时间
    img_show: 是否展示图像, 默认False
    draw_range: 默认 'small'(画2月1日到2日 这两天得图); 'big': 画四个月得图
    """
    # 画图得开始与结束时间 设定:

    if draw_range == 'big':
        draw_start, draw_end = '2019-10-01', '2020-02-14'
    else:
        draw_start, draw_end = '2020-02-01', '2020-02-02'

    ctrl = res[controls[i]]
    prod = res[products[j]]

    plt.figure()  # 绘制没有进行滞后处理的散点图
    ctrl_std = (ctrl - ctrl.mean()) / ctrl.std()

    ctrl_std[draw_start:draw_end].plot(label=controls[i])
    prod_std = (prod - prod.mean()) / prod.std()
    prod_std[draw_start:draw_end].plot(label=products[j])
    plt.title("{}与{}的波动图(未滞后处理)".format(products[j], controls[i]))
    plt.ylabel("正态标准化数值")
    plt.legend()

    plt.savefig('img/滞后/' + "{}与{}的波动图(未滞后处理)".format(products[j], controls[i]))
    if img_show:
        plt.show()
    else:
        plt.close()

    ##  滞后图

    corr_list = []
    for periods in range(lag_min * 60, lag_max * 60 + 1):
        corr_list.append(ctrl.shift(periods).corr(prod))

    plt.figure()
    plt.plot(range(lag_min * 60, lag_max * 60 + 1), np.abs(corr_list))
    plt.xlabel("滞后时间/min")
    plt.ylabel("绝对相关系数")
    np_corr_list = np.abs(np.array(corr_list))

    lag_time = np_corr_list.argmax() + lag_min * 60
    plt.scatter(lag_time, np_corr_list.max(), c='r')

    plt.title("{}与{}的滞后时间分析图(滞后结果:{}min)".format(products[j], controls[i], lag_time))

    print("{}与{}的滞后时间分析图(滞后结果:{}min)".format(products[j], controls[i], lag_time))
    plt.savefig('img/滞后/' + "{}与{}的滞后时间分析图".format(products[j], controls[i], lag_time))
    if img_show:
        plt.show()
    else:
        plt.close()
    ## 滞后处理后的图
    fig_name3 = "{}与{}的波动图(滞后处理后)".format(products[j], controls[i])
    plt.figure()
    ctrl_std[draw_start:draw_end].shift(lag_time).plot(label=controls[i])
    prod_std[draw_start:draw_end].plot(label=products[j])
    plt.title(fig_name3)
    plt.ylabel("正态标准化数值")

    plt.legend()
    plt.savefig('img/滞后/' + fig_name3)
    if img_show:
        plt.show()
    else:
        plt.close()
    return lag_time


if __name__ == "__main__":
    res = get_datas()

    # read config
    config = pd.read_csv('lag_config.lagfig', index_col=0, header=[0, 1]) # lag_config.lagfig 其实是CSV 文件
    controls = config.index
    products = [i[0] for i in config.columns][::2]

    lag_res_table = pd.DataFrame(data=0, index=controls, columns=products)
    for j in range(len(products)):

        for i in range(len(controls)):
            lag_min = config.loc[controls[i], (products[j], 'min')]
            lag_max = config.loc[controls[i], (products[j], 'max')]
            if products[j] in ['焦炭负荷', '[铁水温度]']:  # 对于'焦炭负荷','[铁水温度]' 这样的指标 要画大尺度时间的散点波动图
                lag_res_table.loc[controls[i], products[j]] = lag_analysis(i, j, lag_min, lag_max, draw_range='big')
            else:
                lag_res_table.loc[controls[i], products[j]] = lag_analysis(i, j, lag_min, lag_max)

    # save table to excel
    lag_res_table.to_excel('data/滞后结果表.xlsx')
