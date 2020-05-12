"""
day.py iron.py 等程序的起到环境作用的 module
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from organize2.config.config import PRE_PATH
from organize2.config.config import IRON_TIME


# # excel 文件处理成 pkl文件后 的存放路径
# PRE_PATH = {19: 'data/西昌2#高炉数据19年10-11月/pkl/',
#             20: 'data/西昌2#高炉数据19年12月-20年2月/pkl/',
#             201: 'data/西昌2#高炉数据20年2-4月/pkl/'  # 添加新路径
#
#             }
#
# # 铁次时间表的存放路径
# IRON_TIME = {19: 'data/西昌2#高炉数据19年10-11月/铁次时间.xlsx',
#              20: 'data/西昌2#高炉数据19年12月-20年2月/铁次时间.xlsx',
#              201: 'data/西昌2#高炉数据20年2-4月/铁次时间.xlsx'
#
#              }
#

def find_table(name: str, table: int) -> str or None:
    """
    给出指标 自动寻找在那个表里
    :param name: 要寻找的指标名
    :param table 数据源选择 取值 19 或者 20
    :return 表名
    """

    if table == 19:
        path = 'organize/config/19数据表各个名称罗列.xlsx'
    elif table == 20:
        path = 'organize/config/20数据表各个名称罗列.xlsx'
    else:
        path = 'organize/config/20数据表各个名称罗列.xlsx'
        # print("自动使用[20数据表各个名称罗列.xlsx]")
        # raise Exception("不存在表：{}数据表各个名称罗列.xlsx".format(table))

    dic = pd.read_excel(path)
    temp = dic[dic.isin([name])].dropna(axis=1, how='all')
    if temp.values.shape[1] == 0:
        print("{} :46行警告: 表 {} 无指标 {}".format(__file__, table, name))
        # print("表:", table, "无", name, "!!!!")
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


def get_iron_speed(table):
    """
    利用数据源头中的出铁速率计算，高炉每小时利用系数
    通过出铁速率 计算 每小时高炉利用系数
    :param table: 19 or 20
    :return:
    """
    df_iron_speed = get_df("出铁速率", table)
    df_iron_speed = df_iron_speed.groupby("采集项名称").get_group("出铁速率")
    # 格式化
    df_iron_speed.loc[:, '采集项值'] = pd.to_numeric(df_iron_speed['采集项值'])
    df_iron_speed.loc[:, "业务处理时间"] = pd.to_datetime(df_iron_speed["业务处理时间"])

    # df_iron_speed.loc["业务处理时间"][df_iron_speed['采集项值'] > 1e7] = np.nan
    df_iron_speed.loc[:, "业务处理时间"].where(df_iron_speed['采集项值'] < 1e7, inplace=True)

    df_iron_speed.dropna(inplace=True)

    df_time_indexed = df_iron_speed.set_index("业务处理时间").sort_index()

    time_table = get_time_table(table)
    res = time_table.apply(lambda x: df_time_indexed.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                           axis=1)
    res = res * 60 / 1750
    return res, df_time_indexed


def get_all_iron_speed():
    # 输出两批
    res19, df_time_indexed19 = get_iron_speed(19)
    res20, df_time_indexed20 = get_iron_speed(20)
    ans = pd.concat([res19, res20])

    return ans.to_frame('每小时高炉利用系数')  # change Series to DataFrame

# if __name__ == '__main__':
