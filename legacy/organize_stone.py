# -*- coding: UTF-8 -*-
"""
失败 运行速度太慢
新需求：
整理球团矿比例

球团比例 = 白马球团 / (40赤块+南非块矿+烧结矿+白马球团+酸性烧结矿)

"""
import os
import pandas as pd
from organize.env import get_df
from organize.env import get_time_table


def get_all_data(params_, data_id):
    """
    获取数据 铁次时间表
    :param params_:
    :param data_id:
    :return:
    """
    if isinstance(data_id, int):
        print("只使用了数据批次编码值为%d的数据" % data_id)
        df_ = get_df(params_[0], data_id)
        df_iron_time = get_time_table(data_id)

    elif isinstance(data_id, str):
        if data_id == 'all':  # 导入所以数据
            df19_ = get_df(params_[0], 19)
            df20_ = get_df(params_[0], 20)
            df201_ = get_df(params_[0], 201)
            df_ = pd.concat([df19_, df20_, df201_])

            time_table19 = get_time_table(19)
            time_table20 = get_time_table(20)
            time_table201 = get_time_table(201)
            df_iron_time = pd.concat([time_table19, time_table20, time_table201])
        else:
            raise UserWarning("参数data_id输入错误")
    else:
        raise UserWarning("参数data_id输入错误")
    return df_, df_iron_time


def func(x):
    end = x['受铁开始时间']
    start = x['受铁结束时间']
    # 该铁次下得样本
    block = grouped.where((start < grouped['业务处理时间']) & (grouped['业务处理时间'] < end)).dropna()
    return block['采集项值'].sum()


if __name__ == '__main__':
    os.chdir('../')
    print("work path: ", os.getcwd())
    res = pd.DataFrame()
    param_list = "40赤块 南非块矿 烧结矿 酸性烧结矿 白马球团".split()
    df, iron_time_table = get_all_data(param_list, 'all')

    # 格式化
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
    df['采集项值'] = pd.to_numeric(df['采集项值'])

    param = param_list[0]

    grouped = df.groupby('采集项名称').get_group(param)

    res[param] = iron_time_table.apply(func, axis=1)
