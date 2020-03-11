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

    def __get_df(self, param):
        """
        私有方法: 给出 dataframe 数据
        :param param: 指标名
        :return:
        """
        table_name = find_table(param, self.table)
        path = PRE_PATH[self.table] + table_name + '.pkl'
        df = pd.read_pickle(path)
        return df

    def get_molten_iron(self):
        """
        处理 铁次型数据
        [C],[Ti],[Si],[S],δ[Ti]
        :return:
        """
        df = pd.DataFrame()
        df = self.__get_df('[C]')

        df['铁次号'] = pd.to_numeric(df['铁次号'])
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])  # 格式化
        df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化
        df = df[df['铁次号'] >= 20000000]  # 提取出#2高炉的数据
        df = df[df['铁次号'] < 30000000]

        param_list = ['[C]', '[Ti]', '[Si]', '[S]']
        for param in param_list:
            df_pure = df.groupby("采集项名称").get_group(param)  # 筛选 都在同一个表里
            df_pure = df_pure.groupby('铁次号').mean().rename(columns={'采集项值': param})
            self.res = pd.merge(self.res, df_pure, how="outer", left_index=True, right_index=True)

        return None


if __name__ == "__main__":
    '''
    19年表: 20128288-20129016
    '''
    '''
    铁次型数据
    处理这些
    [C],[Ti],[Si],[S],δ[Ti]
    '''
