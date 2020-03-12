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

PRE_PATH = {19: './data/西昌2#高炉数据19年10-11月/pkl/',
            20: './data/西昌2#高炉数据19年12月-20年2月/pkl/'}


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

        return df_coke, self.res


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
    ans = solv19.get_ratio()
    # 写一个把 业务处理时间改成 铁次号的函数 这样就可以直接用 处理铁次数据的套路了 考虑时间滞后
