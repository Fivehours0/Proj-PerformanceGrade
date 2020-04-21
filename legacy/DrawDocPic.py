# -*- coding: utf-8 -*-
# 绘制高炉操作参数的稳定性范围提取方法的插图

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 修复图片不显示中文的问题
plt.rcParams['axes.unicode_minus'] = False


def outlier():
    # 异常值画图
    param = '炉顶温度1'
    file_name = '西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl'
    path = './data/西昌2#高炉数据19年10-11月/pkl/'

    df = pd.read_pickle(path + file_name)
    df = df.groupby('采集项名称').get_group(param)

    # 数据格式化
    df['业务处理时间'] = df['业务处理时间'].apply(pd.to_datetime)
    df['采集项值'] = df['采集项值'].apply(pd.to_numeric)
    df = df[['业务处理时间', '采集项值']]
    df.set_index('业务处理时间', inplace=True)

    plt.figure(1)
    df.plot()
    plt.title('未进行异常分析的数据波动图')

    plt.figure(2)
    df_after = df.copy()
    df_after['采集项值'][df_after['采集项值'] > 1e7] = None
    df_after.plot()
    plt.title('进行异常分析后的数据波动图')

    return None


def random_forest():
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestClassifier

    ## 随机森林图    
    file = '西昌#2高炉每日整理数据v2.0.xlsx'
    path = './result/'
    df = pd.read_excel(path + file, sheet_name=0, index_col=0)

    x = df.iloc[:, :2].dropna()
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(x)

    y = kmeans.labels_
    x['label'] = y
    df['label'] = x['label']
    df2 = df.dropna()

    forest = RandomForestClassifier(n_estimators=5, random_state=2)
    forest.fit(df2.iloc[:, :30], df2.iloc[:, 30])
    imp = forest.feature_importances_

    plt.barh(range(30), imp)
    plt.yticks(np.arange(30), df2.iloc[:, :30].columns)
    plt.xlabel("Feature importance")
    plt.ylabel("Feature")

    return None


if __name__ == '__main__':
    # 鼓风动能
    param = '鼓风动能'
    file = '西昌2#高炉采集数据表_高炉本体(炉缸1).pkl'
    path = './data/西昌2#高炉数据19年10-11月/pkl/'
    df = pd.read_pickle(path + file)
    df = df.groupby('采集项名称').get_group(param)
    df['采集项值'] = df['采集项值'].apply(pd.to_numeric)
    df['业务处理时间'] = df['业务处理时间'].apply(pd.to_datetime)
    df = df[['业务处理时间', '采集项值']].set_index('业务处理时间')
    df['采集项值'][df['采集项值'] > 1e7] = None
    # 10-15前缺失

    # [Si]
    param = '[Si]'
    file = '铁水成分表.pkl'
    df2 = pd.read_pickle(path + file)
    df2 = df2.groupby('采集项名称').get_group(param)  # 筛选[Si]
    df2['采集项值'] = df2['采集项值'].apply(pd.to_numeric)
    df2['铁次号'] = df2['铁次号'].apply(pd.to_numeric)
    df2_0 = df2.groupby('铁次号').mean()

    df_i = pd.read_excel('./data/西昌2#高炉数据19年10-11月/铁次时间.xlsx')
    df_i['受铁开始时间'] = df_i['受铁开始时间'].apply(pd.to_datetime)
    df_i = df_i.set_index('铁次号')

    df2_0['time'] = df_i['受铁开始时间']
    df2_0 = df2_0.dropna()
    df2 = df2_0.set_index('time')

    # df.rename(columns={'采集项值':'鼓风动能'},inplace=True)
    # df2.rename(columns={'采集项值':'炉喉温度'},inplace=True)

    df.sort_index(inplace=True)
    df2.sort_index(inplace=True)
    tmp = df.loc['2019-10-18':'2019-10-20 0:00']
    tmp2 = df2.loc['2019-10-18':'2019-10-20 0:00']
    from sklearn.preprocessing import StandardScaler

    std = StandardScaler()

    plt.plot(tmp.index, std.fit_transform(tmp), label='鼓风动能')
    plt.plot(tmp2.index, std.fit_transform(tmp2), label='滞后处理前[Si]')
    plt.plot(tmp2.index - pd.Timedelta('240min'), std.fit_transform(tmp2), label='滞后处理后[Si]')
    # plt.title('')
    plt.legend()
    plt.xlabel('时间')
    plt.ylabel('归一化数值')

    # plt.figure(2)
    # plt.plot(tmp.index, std.fit_transform(tmp), label='鼓风动能')

    # plt.title('滞后处理后')
    # plt.legend()
    # plt.xlabel('时间')
    # plt.ylabel('归一化数值')

# tmp2.index - pd.Timedelta('185min')
