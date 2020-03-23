# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 20:07:00 2020

@author: Administrator
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# excel 文件处理成 pkl文件后 的存放路径
PRE_PATH = {19: 'data/西昌2#高炉数据19年10-11月/pkl/',
            20: 'data/西昌2#高炉数据19年12月-20年2月/pkl/'}

# 铁次时间表的存放路径
IRON_TIME = {19: 'data/西昌2#高炉数据19年10-11月/铁次时间.xlsx',
             20: 'data/西昌2#高炉数据19年12月-20年2月/origin/铁次时间.xlsx'}


def find_table(name, table):
    """
    给出指标 自动寻找在那个表里
    :param name: 要寻找的指标名
    :param table 数据源选择 取值 19 或者 20
    :return 表名
    """
    if table == 19:
        path = 'data/19数据表各个名称罗列.xlsx'
    elif table == 20:
        path = 'data/20数据表各个名称罗列.xlsx'
    dic = pd.read_excel(path)
    temp = dic[dic.isin([name])].dropna(axis=1, how='all')
    if temp.values.shape[1] == 0:
        print("表:", table, "无", name, "!!!!")
        return None
    elif temp.values.shape[1] == 1:
        return temp.columns[0]
    elif temp.values.shape[1] > 1:
        print("表:", table, "有大于一个的", name, "自动返回发现的第一个")
        return temp.columns[0]


def get_df(param, table):
    """
    给出 dataframe 数据
    :param param: 指标名
    :param table: 19年 还是 20 年的表 
    :return:
    """
    table_name = find_table(param, table)
    path = PRE_PATH[table] + table_name + '.pkl'
    df = pd.read_pickle(path)

    # 为了去除冗余
    if '系统接收时间' in df.columns:
        df.drop(columns='系统接收时间', inplace=True)
    df.drop_duplicates(inplace=True)

    return df

if __name__ == '__main__':
    
    """
    直接找 同一采集时刻下的 探尺探测段的数据有点少。
    """
    
    time_table = pd.read_excel(IRON_TIME[19])

    # 格式化
    time_table['受铁开始时间'] = time_table['受铁开始时间'].astype('datetime64')
    time_table['受铁结束时间'] = time_table['受铁结束时间'].astype('datetime64')
    time_table['铁次号'] = time_table['铁次号'].astype('int64')

    # 提取出#2高炉的数据
    time_table = time_table[time_table['铁次号'] >= 20000000]
    time_table = time_table[time_table['铁次号'] < 30000000]
    time_table = time_table.set_index('铁次号').sort_index()
    
    
    
    df = get_df('探尺（东）',19)
    df['采集项值'] = pd.to_numeric(df['采集项值'])
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])   
    
    brothel = ['探尺（南）', '探尺（东）', '探尺（西）']
    hookers = []
    for hooker_name in brothel:
        hooker = df.groupby('采集项名称').get_group(hooker_name).set_index('业务处理时间')  # 筛选
        
        hooker.drop(columns=['采集项编码', '采集项名称'], inplace=True)
        hooker.rename(columns={'采集项值': hooker_name}, inplace=True)
        hooker[hooker_name][hooker[hooker_name] > 1e7] = None  # 去除1e7 的异常值
        hooker['delta_time'] = np.nan
        hooker['delta_time'].iloc[1:] =  hooker.index[1:] - hooker.index[:-1]
        
        hooker[hooker_name][hooker[hooker_name] < 0] = np.nan
        hooker.dropna(inplace=True)
        
        hooker['delta_time'][hooker['delta_time'] < pd.Timedelta('60s')] = np.nan
        hooker.dropna(inplace=True)        

        hookers.append(hooker)    

     # 找出 所有 在同一时刻 三个探尺高度数据都不缺失的样本
    temp = pd.merge(hookers[0], hookers[1], how="inner", left_index=True, right_index=True)
    blondie = pd.merge(temp, hookers[2], how="inner", left_index=True, right_index=True)   

        # 计算极差
    wife = pd.DataFrame()
    wife['采集项值'] = blondie.max(axis=1) - blondie.min(axis=1)
    res = pd.DataFrame()
    res['探尺差'] = time_table.iloc[3:].apply(lambda x: wife.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                                axis=1)
    
    # draw = grouped.loc['2019-10-15 12:00:00':'2019-10-15 12:30:00','采集项值']
    # draw.plot()
    # plt.scatter(draw.index,draw.values,c='r')
