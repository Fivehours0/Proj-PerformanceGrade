"""
:describe 按照铁次整理数据
:author 夏尚梓
:version v1.0
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# excel 文件处理成 pkl文件后 的存放路径
PRE_PATH = {19: './data/西昌2#高炉数据19年10-11月/pkl/',
            20: './data/西昌2#高炉数据19年12月-20年2月/pkl/'}
# 铁次时间表的存放路径
IRON_TIME = {19: './data/西昌2#高炉数据19年10-11月/铁次时间.xlsx',
             20: './data/西昌2#高炉数据19年12月-20年2月/origin/铁次时间.xlsx'}


def find_table(name, table):
    """
    给出指标 自动寻找在那个表里
    """
    if table == 19:
        path = './19数据表各个名称罗列.xlsx'
    elif table == 20:
        path = './20数据表各个名称罗列.xlsx'
    dic = pd.read_excel(path)
    return dic[dic.isin([name])].dropna(axis=1, how='all').columns[0]


def time2order(df, table, five_lag=False):
    """
    :param five_lag: 是否滞后, 将业务处理时间推前5小时
    :param df: 要生成铁次号的 DataFrame
    :param table: 同 Solution.__init__()
    :return: 添加了 铁次号的 DataFrame
    """
    df['业务处理时间'] = df['业务处理时间'].astype('datetime64')
    df.sort_values('业务处理时间', inplace=True)

    df['铁次号'] = 0
    if five_lag:
        df['业务处理时间'] = df['业务处理时间'] - pd.to_timedelta('5h')

    time = df['业务处理时间']  # 注意 temp 与 df['业务处理时间'] 一个地址
    time_table = pd.read_excel(IRON_TIME[table])
    time_table['受铁开始时间'] = time_table['受铁开始时间'].astype('datetime64')
    time_table['受铁结束时间'] = time_table['受铁结束时间'].astype('datetime64')
    time_table['铁次号'] = time_table['铁次号'].astype('int64')
    time_table = time_table[time_table['铁次号'] >= 20000000]  # 提取出#2高炉的数据
    time_table = time_table[time_table['铁次号'] < 30000000]

    for i in range(time_table.shape[0]):
        start, end = time_table.iloc[i, 1], time_table.iloc[i, 2]
        df.loc[time[start < time][time < end].index, '铁次号'] = time_table.iloc[i, 0]
    return df


class Solution:
    def __init__(self, table):
        """
        初始化
        :param table: 数据源选择 取值 19 或者 20
        """
        self.table = table
        self.res = pd.DataFrame()

    def get_df(self, param):
        """
        给出 dataframe 数据
        :param param: 指标名
        :return:
        """
        table_name = find_table(param, self.table)
        path = PRE_PATH[self.table] + table_name + '.pkl'
        df = pd.read_pickle(path)
        return df

    def process_iron(self, param_list, agg_func):
        """
        对铁次型数据 预处理
        :param agg_func: 聚合函数 传入类型: 一个函数对象
        :param param_list: 要处理的指标列表 类型: list
        :return:None
        """
        df = pd.DataFrame()
        df = self.get_df(param_list[0])

        df['铁次号'] = pd.to_numeric(df['铁次号'])
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])  # 格式化
        df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化
        df = df[df['铁次号'] >= 20000000]  # 提取出#2高炉的数据
        df = df[df['铁次号'] < 30000000]

        # 这里假设 param_list 中的指标都在一个表里
        for param in param_list:
            df_pure = df.groupby("采集项名称").get_group(param)  # 筛选 都在同一个表里
            df_pure = df_pure.groupby('铁次号').agg(agg_func).rename(columns={'采集项值': param})
            self.res = pd.merge(self.res, df_pure, how="outer", left_index=True, right_index=True)
        return None

    def get_molten_iron(self):
        """
        '[C]', '[Ti]', '[Si]', '[S]'
        :return:
        """
        param_list = ['[C]', '[Ti]', '[Si]', '[S]']
        self.process_iron(param_list, np.mean)
        return None

    def get_slag(self):
        """
        (TiO2) (SiO2) (CaO) (MgO) (Al2O3)
        R2 = CaO/SiO2  R3 = (CaO+MgO)/SiO2  R4 = (CaO+MgO)/(SiO2+Al2O3) 镁铝比 = MgO / Al2O3
        δR2 搞不了
        :return:
        """
        param_list = ['(TiO2)', '(SiO2)', '(CaO)', '(MgO)', '(Al2O3)']
        self.process_iron(param_list, np.mean)

        self.res['R2'] = self.res['(CaO)'] / self.res['(SiO2)']
        self.res['R3'] = (self.res['(CaO)'] + self.res['(MgO)']) / self.res['(SiO2)']
        self.res['R4'] = (self.res['(CaO)'] + self.res['(MgO)']) / (self.res['(SiO2)'] + self.res['(Al2O3)'])
        self.res['镁铝比'] = self.res['(MgO)'] / self.res['(Al2O3)']  # 有一条明显比较怪的数据, 需要后期核查

        return None

    def get_ratio(self):
        """
        铁次铁量,喷吹速率,焦比,煤比,燃料比
        :return:
        """
        # 计算铁量
        self.process_iron(['受铁重量'], np.sum)
        self.res.rename(columns={'受铁重量': '铁次铁量'}, inplace=True)  # 发现有一些铁次铁量是 0, 需要后期核查

        # 计算焦量
        param_list = ['冶金焦（自产）', '小块焦']
        param = param_list[0]
        df_coke = self.get_df(param)
        df_coke = time2order(df_coke, self.table)
        return df_coke


def main():
    solv19 = Solution(19)
    solv19.get_molten_iron()
    solv19.get_slag()

    solv20 = Solution(20)
    solv20.get_molten_iron()
    solv20.get_slag()

    ans = pd.concat([solv19.res, solv20.res])


if __name__ == "__main__":
    '''
    19年表: 20128288-20129016
    '''
    solv19 = Solution(19)

    df = solv19.get_df('炉顶压力1')
    df = df.groupby("采集项名称").get_group('炉顶压力1')

    df['采集项值'] = df['采集项值'].apply(pd.to_numeric)
    df['业务处理时间'] = df['业务处理时间'].astype('datetime64')
    df = df[['采集项值', '业务处理时间']]
    df = df.set_index('业务处理时间').sort_index()

    df = df.resample('1T').mean()  # 缩小数据大小 1分钟 一次的
    # df['铁次号'] = 0
    table = 19
    # time = df['业务处理时间']  # 注意 temp 与 df['业务处理时间'] 一个地址
    time_table = pd.read_excel(IRON_TIME[table])
    time_table['受铁开始时间'] = time_table['受铁开始时间'].astype('datetime64')
    time_table['受铁结束时间'] = time_table['受铁结束时间'].astype('datetime64')
    time_table['铁次号'] = time_table['铁次号'].astype('int64')
    time_table = time_table[time_table['铁次号'] >= 20000000]  # 提取出#2高炉的数据
    time_table = time_table[time_table['铁次号'] < 30000000]
    time_table = time_table.set_index('铁次号').sort_index()
    #
    # res = pd.DataFrame(data=0, index=time_table['铁次号'], columns=['炉顶压力1'])
    res = pd.DataFrame()


    def func(x):
        start, end = x['受铁开始时间'], x['受铁结束时间']
        return df.loc[start:end, '采集项值'].mean()
    res['炉顶压力1'] = time_table.apply(func, axis=1)
    # for i in range(time_table.shape[0]):
    #     start, end = time_table.iloc[i, 1], time_table.iloc[i, 2]
    #     df.loc[start:end,'采集项值'].mean()
    #     df.loc[time[start < time][time < end].index, '铁次号'] = time_table.iloc[i, 0]

    # def func(x):
    #
    #     def func2(y):
    #         if y.受铁开始时间 <= time <= y.受铁结束时间:
    #             return y['铁次号']
    #         else:
    #             return None
    #
    #     time = x
    #     try:
    #         ans = time_table.apply(func2, axis=1).dropna()[0]
    #     except(KeyError, IndexError):
    #         ans = None
    #     return ans
    #

    # df = pd.DataFrame(data=None, index=df['业务处理时间'])
    # df['铁次号'] = 0
    # t_idx = 0
    # for idx, item in enumerate(df.index):
    #     if  < item

    # ans = df.resample('1T').mean()
    # df.set_index('业务处理时间', inplace=True)
    # ans = df.groupby(func).agg(np.mean)
    # ans = time2order(df,19)
