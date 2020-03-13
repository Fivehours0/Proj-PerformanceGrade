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
    :param name: 要寻找的指标名
    :param table 数据源选择 取值 19 或者 20
    :return 表名
    """
    if table == 19:
        path = './19数据表各个名称罗列.xlsx'
    elif table == 20:
        path = './20数据表各个名称罗列.xlsx'
    dic = pd.read_excel(path)
    return dic[dic.isin([name])].dropna(axis=1, how='all').columns[0]


class Solution:
    def __init__(self, table):
        """
        初始化
        :param table: 数据源选择 取值 19 或者 20
        """
        self.table = table
        self.res = pd.DataFrame()
        self.time_table = self.get_time_table()

    def get_time_table(self):
        """
        获取 铁次时间表的 DataFrame 型
        其中 index 是其 铁次
        :return:
        """
        time_table = pd.read_excel(IRON_TIME[self.table])

        # 格式化
        time_table['受铁开始时间'] = time_table['受铁开始时间'].astype('datetime64')
        time_table['受铁结束时间'] = time_table['受铁结束时间'].astype('datetime64')
        time_table['铁次号'] = time_table['铁次号'].astype('int64')

        # 提取出#2高炉的数据
        time_table = time_table[time_table['铁次号'] >= 20000000]
        time_table = time_table[time_table['铁次号'] < 30000000]
        time_table = time_table.set_index('铁次号').sort_index()

        return time_table

    def time2order(self, df, five_lag=False):
        """
        :param five_lag: 是否滞后, 将业务处理时间推前5小时
        :param df: 要生成铁次号的 DataFrame
        :return: 添加了 铁次号的 DataFrame
        """
        df['业务处理时间'] = df['业务处理时间'].astype('datetime64')
        df.sort_values('业务处理时间', inplace=True)
        df['铁次号'] = 0
        if five_lag:
            df['业务处理时间'] = df['业务处理时间'] - pd.to_timedelta('5h')
        time = df['业务处理时间']  # 注意 temp 与 df['业务处理时间'] 一个地址
        for i in range(self.time_table.shape[0]):
            start, end = self.time_table['受铁开始时间'].iloc[i], self.time_table['受铁结束时间'].iloc[i]
            df.loc[time[start < time][time < end].index, '铁次号'] = self.time_table.index[i]
        return df

    def process_big_time(self, param, df=None):
        """
        适合数据量 100万以上的
        :param df: 传入大型DateFrame
        :param param: 要被处理的单个指标 , 或者多指标
        :return:
        """
        res = pd.DataFrame()
        mul_option = isinstance(param, list)  # mul_option: 多指标是否同时在本函数里处理?
        if not mul_option:
            df = self.get_df(param)  # param = '炉顶压力1' 比如炉顶压力这种
            df = df.groupby("采集项名称").get_group(param)
            df['采集项值'] = df['采集项值'].apply(pd.to_numeric)
            df['业务处理时间'] = df['业务处理时间'].astype('datetime64')
            df = df[['采集项值', '业务处理时间']]
            df = df.set_index('业务处理时间').sort_index()
            df['采集项值'][df['采集项值'] > 1e7] = None  # 去除 999999 的异常值

            # def func(x):
            #     start, end = x['受铁开始时间'], x['受铁结束时间']
            #     return df.loc[start:end, '采集项值'].mean()
            res[param] = self.time_table.apply(lambda x: df.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                               axis=1)
            return res
        else:
            df['采集项值'] = df['采集项值'].apply(pd.to_numeric)
            df['业务处理时间'] = df['业务处理时间'].astype('datetime64')

            df['采集项值'][df['采集项值'] > 1e7] = None  # 去除 999999 的异常值

            for item in param:
                df_grouped = df.groupby("采集项名称").get_group(item)
                df_grouped = df_grouped[['采集项值', '业务处理时间']]

                df_grouped = df_grouped.set_index('业务处理时间').sort_index()
                df_rsp = df_grouped.resample('1T').mean()  # 缩小数据大小 1分钟 一次的

                res[item] = self.time_table.apply(lambda x: df_rsp.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                                  axis=1)
            return res

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

    def process_iron(self, df, param_list, agg_func):
        """
        对铁次型数据 预处理
        :param df: 要传入的表
        :param agg_func: 聚合函数 传入类型: 一个函数对象
        :param param_list: 要处理的指标列表 类型: list
        :return:
        """
        res = pd.DataFrame()
        # df = self.get_df(param_list[0])

        df['铁次号'] = pd.to_numeric(df['铁次号'])
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])  # 格式化
        df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化
        df = df[df['铁次号'] >= 20000000]  # 提取出#2高炉的数据
        df = df[df['铁次号'] < 30000000]

        # 这里假设 param_list 中的指标都在一个表里
        for param in param_list:
            df_pure = df.groupby("采集项名称").get_group(param)  # 筛选 都在同一个表里
            df_pure = df_pure.groupby('铁次号').agg(agg_func).rename(columns={'采集项值': param})
            res = pd.merge(res, df_pure, how="outer", left_index=True, right_index=True)
        return res

    def get_molten_iron(self):
        """
        '[C]', '[Ti]', '[Si]', '[S]'
        :return:
        """
        param_list = ['[C]', '[Ti]', '[Si]', '[S]']
        df = self.get_df(param_list[0])
        res = self.process_iron(df, param_list, np.mean)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_slag(self):
        """
        (TiO2) (SiO2) (CaO) (MgO) (Al2O3)
        R2 = CaO/SiO2  R3 = (CaO+MgO)/SiO2  R4 = (CaO+MgO)/(SiO2+Al2O3) 镁铝比 = MgO / Al2O3
        δR2 搞不了
        :return:
        """
        param_list = ['(TiO2)', '(SiO2)', '(CaO)', '(MgO)', '(Al2O3)']
        df = self.get_df(param_list[0])
        res = self.process_iron(df, param_list, np.mean)

        res['R2'] = res['(CaO)'] / res['(SiO2)']
        res['R3'] = (res['(CaO)'] + res['(MgO)']) / res['(SiO2)']
        res['R4'] = (res['(CaO)'] + res['(MgO)']) / (res['(SiO2)'] + res['(Al2O3)'])
        res['镁铝比'] = res['(MgO)'] / res['(Al2O3)']  # 有一条明显比较怪的数据, 需要后期核查

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_ratio(self):
        """
        铁次铁量,喷吹速率,焦比,煤比,燃料比,出铁次数/出铁时间
        :return:
        """
        # 计算铁量
        df = self.get_df('受铁重量')
        res = self.process_iron(df, ['受铁重量'], np.sum)
        res.rename(columns={'受铁重量': '铁次铁量'}, inplace=True)  # 发现有一些铁次铁量是 0, 需要后期核查

        # 计算焦量, 焦比
        param_list = ['冶金焦（自产）', '小块焦']
        param = param_list[0]
        df_coke = self.get_df(param)
        df_coke = self.time2order(df_coke, five_lag=False)
        df_coke = self.process_iron(df_coke, param_list, np.sum)
        res['焦比'] = (df_coke['冶金焦（自产）'] + df_coke['小块焦']) / res['铁次铁量'] * 1000

        # 计算喷煤 煤比
        df_mei = self.process_big_time('喷吹速率')
        d = self.time_table['受铁结束时间'] - self.time_table['受铁开始时间']
        df_mei['d'] = d / pd.to_timedelta('1min')

        res['喷吹速率'] = df_mei['喷吹速率']
        res['出铁次数/出铁时间,min'] = df_mei['d']
        res['煤比'] = df_mei['d'] * df_mei['喷吹速率'] / res['铁次铁量'] * 20
        # 燃料比
        res['燃料比'] = res['煤比'] + res['焦比']

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_wind(self):
        """
        送风风量,热风压力,炉顶压力,标准风速,热风温度
        实际风速 = 标准风速*(0.101325/273)*((273+风温)/(风压/10+0.101325))
        透气性指数 = 送风风量 / (热风压力 - 炉顶压力1,2) * 100
        :return:
        """
        res = self.process_big_time(['送风风量', '热风压力', '标准风速', '热风温度'], self.get_df('送风风量'))
        res2 = self.process_big_time(['炉顶压力1', '炉顶压力2'], self.get_df('炉顶压力1'))
        res['炉顶压力'] = res2.mean(axis=1)
        res['实际风速'] = res['标准风速'] * (0.101325 / 273) * ((273 + res['热风温度']) / (res['热风压力'] / 1000 + 0.101325))
        res['透气性指数'] = res['送风风量'] / (res['热风压力'] - res['炉顶压力']) * 100
        return res, res2


def main():
    solv19 = Solution(19)
    solv19.get_molten_iron()
    solv19.get_slag()
    solv19.get_ratio()

    solv20 = Solution(20)
    solv20.get_molten_iron()
    solv20.get_slag()
    solv20.get_ratio()
    ans = pd.concat([solv19.res, solv20.res])
    ans.to_excel("铁次结果.xlsx")  # 因为铁次产量为0 搞出不少 inf
    return ans


if __name__ == "__main__":
    '''
    19年表: 20128288-20129016
    '''
    # ans = main()
    solv19 = Solution(19)
    ans = solv19.get_wind()
