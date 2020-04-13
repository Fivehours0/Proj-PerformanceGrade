"""
需求变更 暂时不处理100的了


处理出每日数据， 数据是天得不用考虑滞后

指标
完整版本
再从完整版本抽出钢铁研究院版本

包括上 异常处理 缺失填充
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mymo.get_things import find_table
from mymo.get_things import get_df
from mymo.get_things import get_time_table
from mymo.iron_product_speed import get_iron_speed

#  需要丢弃离群点的参数，其取值范围
OUTLIERS_RANGE = {
    'R2': [0, 14],
    'R3': [0, 14],
    '炉顶煤气CO': [20, 30],
    '炉顶煤气CO2': [15, 25],
    '炉顶温度极差': [-1, 200],
    'deltaR2': [-10, 10]
}

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def get_df_format(input_param, input_table):
    """
    获取指标含有指标数据表时 处理好格式
    :param input_table:
    :param input_param:
    :return:
    """
    df_ = get_df(input_param, input_table)
    if '业务处理时间' in df_.columns:
        df_['业务处理时间'] = df_['业务处理时间'].apply(pd.to_datetime)
        df_['业务处理时间'] = df_['业务处理时间'].dt.floor('d')  # 时间对天取整数
    if '采集项值' in df_.columns:
        df_['采集项值'] = df_['采集项值'].apply(pd.to_numeric)
    if '铁次号' in df_.columns and df_['铁次号'][0] != ' ':
        df_['铁次号'] = df_['铁次号'].apply(pd.to_numeric)

        # 提取出#2高炉的数据
        df_ = df_[df_['铁次号'] >= 20000000]
        df_ = df_[df_['铁次号'] < 30000000]
        df_.sort_values('铁次号', inplace=True)

    return df_


def process_easy(param_, table_, agg_func):
    """
    直接聚合
    """
    df = get_df_format(param_, table_)
    temp = df.groupby('采集项名称').get_group(param_)
    res_ = temp.groupby('业务处理时间').apply(agg_func)
    res_.rename(columns={'采集项值': param_}, inplace=True)
    return res_[param_]


def get_deltaTi(table):
    """
    
    :return: 
    """
    return None

if __name__ == '__main__':
    table = 19
    param = '焦炭粒度、冷强度_M40'
    res = process_easy(param, table, np.mean)
    #         输出结果表名     SQL中字段名
    list_cmp="M40             焦炭粒度、冷强度_M40 \
              M10             焦炭粒度、冷强度_M10 \
              CRI             焦炭热性能_CRI \
              CSR             焦炭热性能_CSR \
              St              焦炭工分_St \
              Ad              焦炭工分_Ad \
              Mt              焦炭水分_Mt \
              喷吹煤Ad,%       喷吹煤粉_Ad \
              喷吹煤St，%      喷吹煤粉_St \
              喷吹煤Vd，%      喷吹煤粉_Vdaf \
             烧结矿转鼓强度,%  烧结矿性能样(粒度、强度)_转鼓指数 \
             [C]               [C] \
              [Ti] [Ti] \
             [Si] [Si] \
              [S] [S]".split()
    # list0 = ['焦炭粒度、冷强度_M10',
    #          '焦炭工分_St',
    #          '焦炭热性能_CRI',
    #          '焦炭热性能_CSR',
    #          '焦炭工分_Ad',
    #          '焦炭水分_Mt',
    #          '[C]', '[Ti]', '[Si]', '[S]'
    #          ]
    list0 = list_cmp[::2]
    list1 = list_cmp[1::2]
    for item in list0:
        temp = process_easy(item, table, np.mean)
        res = pd.merge(res, temp, 'outer', left_index=True, right_index=True)
