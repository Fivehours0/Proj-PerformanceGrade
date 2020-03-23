import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

"""
如果有新的数据来的时候需要拓展！！！
"""
# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# excel 文件处理成 pkl文件后 的存放路径
PRE_PATH = {19: 'data/西昌2#高炉数据19年10-11月/pkl/',
            20: 'data/西昌2#高炉数据19年12月-20年2月/pkl/'}

# 铁次时间表的存放路径
IRON_TIME = {19: 'data/西昌2#高炉数据19年10-11月/铁次时间.xlsx',
             20: 'data/西昌2#高炉数据19年12月-20年2月/origin/铁次时间.xlsx'}


def find_table(name: str, table: int) -> str or None:
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
    else:
        raise Exception("不存在表：{}数据表各个名称罗列.xlsx".format(table))

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


def get_df(param: str, table: int) -> pd.DataFrame:
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


def get_time_table(table: int) -> pd.DataFrame:
    """
    获取 铁次时间表的 DataFrame 型, 并且把 铁次号设为index
    :param table

    :return:
    """
    time_table = pd.read_excel(IRON_TIME[table])

    # 格式化
    time_table['受铁开始时间'] = time_table['受铁开始时间'].astype('datetime64')
    time_table['受铁结束时间'] = time_table['受铁结束时间'].astype('datetime64')
    time_table['铁次号'] = time_table['铁次号'].astype('int64')

    # 提取出#2高炉的数据
    time_table = time_table[time_table['铁次号'] >= 20000000]
    time_table = time_table[time_table['铁次号'] < 30000000]
    time_table = time_table.set_index('铁次号').sort_index()

    return time_table
