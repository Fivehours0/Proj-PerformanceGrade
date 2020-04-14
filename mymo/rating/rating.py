"""
打分模块程序 alpha 版本

读取excel表的数据

打分项目暂定钢研院给的40+指标


暂时对“铁次”打分。or 实时打分？
"""
import pandas as pd
import numpy as np
from mymo.get_things import get_df


def get_df_format(input_param, input_table):
    """
    获取指标含有指标数据表时 处理好格式
    :param input_table:
    :param input_param:
    :return:
    """
    df_ = get_df(input_param, input_table)
    if '业务处理时间' in df_.columns:
        df_['业务处理时间'] = df_['业务处理时间'].astype('datetime64')
    if '采集项值' in df_.columns:
        df_['采集项值'] = df_['采集项值'].apply(pd.to_numeric)
    if '铁次号' in df_.columns:
        df_['铁次号'] = df_['铁次号'].astype('int64')

        # 提取出#2高炉的数据
        df_ = df_[df_['铁次号'] >= 20000000]
        df_ = df_[df_['铁次号'] < 30000000]
        df_.sort_values('铁次号', inplace=True)

    return df_


if __name__ == '__main__':
    score = 0
    rating_table = pd.read_excel('mymo/rating/打分范围.xlsx', index_col=0)
    rating_table.iloc[:, [1, 3, 5, 7]] = rating_table.iloc[:, [1, 3, 5, 7]].replace('/', -1 * np.inf)  # '/' -> -inf
    rating_table.iloc[:, [0, 2, 4, 6]] = rating_table.iloc[:, [0, 2, 4, 6]].replace('/', np.inf)  # '/' -> inf
    # now_time = '2020-01-01 00:00:00'

    param = '(TiO2)'
    df = get_df_format(param, 20)
    df_param = df.where(df.采集项名称 == param).dropna()

    iorn_order = 20129936

    df_param.set_index('铁次号', inplace=True)
    value = df_param.loc[iorn_order, '采集项值']

    if rating_table.loc[param, '100-'] < value < rating_table.loc[param, '100+']:
        score += 100
    elif rating_table.loc[param, '90-'] < value < rating_table.loc[param, '90+']:
        score += 90
    elif rating_table.loc[param, '75-'] < value < rating_table.loc[param, '75+']:
        score += 75
    elif rating_table.loc[param, '65-'] < value < rating_table.loc[param, '65+']:
        score += 65
    else:
        score += 0

    print(score)
