"""
利用数据源头中的出铁速率计算，高炉每小时利用系数

"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mymo.get_things import get_df
from mymo.get_things import get_time_table

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def get_iron_speed(table):
    """
    通过出铁速率 计算 每小时高炉利用系数
    :param table: 19 or 20
    :return:
    """
    df_iron_speed = get_df("出铁速率", table)
    df_iron_speed = df_iron_speed.groupby("采集项名称").get_group("出铁速率")
    # 格式化
    df_iron_speed['采集项值'] = pd.to_numeric(df_iron_speed['采集项值'])
    df_iron_speed["业务处理时间"] = pd.to_datetime(df_iron_speed["业务处理时间"])
    df_iron_speed["业务处理时间"][df_iron_speed['采集项值'] > 1e7] = np.nan
    df_iron_speed.dropna(inplace=True)

    df_time_indexed = df_iron_speed.set_index("业务处理时间").sort_index()

    # df_time_indexed['采集项值'].plot()
    # plt.show()
    time_table = get_time_table(table)
    res = time_table.apply(lambda x: df_time_indexed.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                           axis=1)
    res = res * 60 / 1750
    # plt.scatter(res.index, res.values)
    # plt.show()
    return res, df_time_indexed


def get_all_iron_speed():
    # 输出两批
    res19, df_time_indexed19 = get_iron_speed(19)
    res20, df_time_indexed20 = get_iron_speed(20)
    ans = pd.concat([res19, res20])

    return ans.to_frame('每小时高炉利用系数')  # change Series to DataFrame

# if __name__ == '__main__':


# # 分析采集频率是否均匀
# df_time_indexed19['time'] = df_time_indexed19.index
# df_time_indexed20['time'] = df_time_indexed20.index
# df_time_indexed19['time_diff'] = df_time_indexed19['time'].diff()
# df_time_indexed20['time_diff'] = df_time_indexed20['time'].diff()
# # 采集频率 再 1min 与 1hour 比较均匀
