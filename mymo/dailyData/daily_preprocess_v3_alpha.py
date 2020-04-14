"""
create time : 2020-04-13 22:57:00
author: xsz
version: v3 alpha
description:

目标：进行 100每日指标整理

并且完成 46，21指标的抽取

以及后面的缺失异常去除

依赖： 三批数据源的pkl文件， 名称罗列表


"""
import numpy as np
import pandas as pd
from mymo.get_things import get_df
from matplotlib import pyplot as plt


class Solution:
    def __init__(self, input_table):
        self.table = input_table
        self.res = pd.DataFrame()

    def process_easy(self, param_list, agg_func=np.mean):
        """
        简单的取平均的指标，通用处理模板
        :param param_list 指标集合，必须在同一个excel文件中
        :param table 表的代码
        :param agg_func 聚合函数 默认取平均
        """
        res = pd.DataFrame()
        df = self.get_df_format(param_list[0])

        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param)
            temp1 = temp.groupby('业务处理时间').apply(agg_func)
            res[param] = temp1['采集项值'].copy()
        return res

    def get_df_format(self, input_param):
        """
        获取指标含有指标数据表时 处理好格式
        :param input_table:
        :param input_param:
        :return:
        """
        df_ = get_df(input_param, self.table)
        if '业务处理时间' in df_.columns:
            df_['业务处理时间'] = df_['业务处理时间'].apply(pd.to_datetime)
            df_['业务处理时间'] = df_['业务处理时间'].dt.floor('d')  # 时间对天取整数
        if '采集项值' in df_.columns:
            df_['采集项值'] = df_['采集项值'].apply(pd.to_numeric)
            # 在这进行 去除999的操作
            df_['采集项值'][df_['采集项值'] > 1e7] = np.nan

        if '铁次号' in df_.columns and df_['铁次号'][0] != ' ':
            df_['铁次号'] = df_['铁次号'].apply(pd.to_numeric)

            # 提取出#2高炉的数据
            df_ = df_[df_['铁次号'] >= 20000000]
            df_ = df_[df_['铁次号'] < 30000000]
            df_.sort_values('铁次号', inplace=True)

        return df_

    def get_coke(self):
        # 上料质量表

        param_list = "焦炭粒度、冷强度_M40  焦炭粒度、冷强度_M10  焦炭工分_St 焦炭热性能_CRI  焦炭热性能_CSR  焦炭工分_Ad 焦炭水分_Mt " \
                     " 高炉沟下烧结矿粒度_筛分指数(<5mm) 喷吹煤粉_Ad 喷吹煤粉_Mt 喷吹煤粉_Vdaf 烧结矿性能样(粒度、强度)_转鼓指数".split()
        # param_list_id = [34, 35, 38, 36, 37]
        res = self.process_easy(param_list)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_molten_iron(self):
        # 西昌2#高炉-铁水成分表
        param_list = ['[C]', '[Ti]', '[Si]', '[S]']
        res = self.process_easy(param_list)
        res['[Si]+[Ti]'] = res['[Si]'] + res['[Ti]']
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_deltaTi(self):
        res = pd.DataFrame()
        param = '[Ti]'
        df = self.get_df_format(param)

        Ti = df.groupby('采集项名称').get_group(param)  # 筛选出Ti
        Ti = Ti.groupby('铁次号').mean()

        Ti = Ti.diff()
        # 处理过程中 业务处理日期丢了 此段代码负责找补回来 # ΔR2 算错了
        tvo = df.loc[:, ['业务处理时间', '铁次号']]
        tvo2 = tvo.drop_duplicates()
        tvo2 = tvo2.set_index('铁次号')
        nTi = pd.merge(Ti, tvo2, right_index=True, left_index=True)

        res['delta_Ti'] = nTi.groupby('业务处理时间').mean()['采集项值']

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_slag(self):
        res = pd.DataFrame()
        param_list = [
            '(CaO)',
            '(SiO2)',
            '(MgO)',
            '(TiO2)',
            '(Al2O3)']

        df = self.get_df_format(param_list[0])
        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param)
            temp1 = temp.groupby('业务处理时间').mean()
            res[param] = temp1['采集项值'].copy()

        res['R2'] = res['(CaO)'] / res['(SiO2)']
        res['R3'] = (res['(CaO)'] + res['(MgO)']) / res['(SiO2)']
        res['镁铝比'] = res['(MgO)'] / res['(Al2O3)']
        res['R4'] = (res['(CaO)'] + res['(MgO)']) / (res['(SiO2)'] + res['(Al2O3)'])
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_deltaR2(self):
        # 计算delta_R2
        # 计算方法 后一个铁次减去前一个铁次 在对天取平均
        res = pd.DataFrame()

        df = self.get_df_format('(CaO)')

        CaO = df.groupby('采集项名称').get_group('(CaO)')  # 筛选
        CaO = CaO.groupby('铁次号').mean()

        SiO2 = df.groupby('采集项名称').get_group('(SiO2)')  # 筛选
        SiO2 = SiO2.groupby('铁次号').mean()
        R2 = CaO / SiO2
        R2 = R2.diff()
        # 处理过程中 业务处理日期丢了 此段代码负责找补回来 # ΔR2 算错了
        tvo = df.loc[:, ['业务处理时间', '铁次号']]
        tvo2 = tvo.drop_duplicates()
        tvo2 = tvo2.set_index('铁次号')
        nR2 = pd.merge(R2, tvo2, right_index=True, left_index=True)

        res['delta_R2'] = nR2.groupby('业务处理时间').mean()['采集项值']

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_ratio(self):
        res = pd.DataFrame()

        ## 日产量
        df = self.get_df_format('受铁重量')
        # df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        # df['采集项值'] = pd.to_numeric(df['采集项值'])
        res['日产量'] = df.groupby('业务处理时间').sum()['采集项值']

        ### 焦比
        df = self.get_df_format('冶金焦（自产）')
        df1 = df.groupby('采集项名称').get_group('冶金焦（自产）')
        df2 = df.groupby('采集项名称').get_group('小块焦')

        res['焦比'] = df1.groupby('业务处理时间').sum()['采集项值'] \
                    + df2.groupby('业务处理时间').sum()['采集项值']
        res['焦比'] = res['焦比'] / res['日产量'] * 1000

        # #  煤比   # 煤比有问题
        param = '喷吹速率'

        df = self.get_df_format(param)
        df2 = df.groupby('采集项名称').get_group(param)
        # 999999 异常值处理
        df2['采集项值'][df2['采集项值'] > 1e7] = np.nan

        res['喷吹速率'] = df2.groupby('业务处理时间').mean()['采集项值']  # 先求每日的均值
        res['日喷煤量'] = res['喷吹速率'] * 24 * 60  # 每分钟喷煤量 * 24小时 * 60分钟
        # temp = df.groupby('业务处理时间').apply(np.max)
        res['煤比'] = res['日喷煤量'] / res['日产量'] * 20

        res['燃料比'] = res['焦比'] + res['煤比']
        res['粉焦比'] = res['煤比'] / res['焦比']
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_loading(self):
        """
        上料系统
         '炉顶压力1', '炉顶压力2', '焦炭负荷'

        """
        res = pd.DataFrame()
        param_list = ['焦炭负荷', '炉顶压力1', '炉顶压力2']
        pre_res = self.process_easy(param_list)
        res['焦炭负荷'] = pre_res['焦炭负荷']
        res['炉顶压力'] = pre_res[['炉顶压力1', '炉顶压力2']].mean(axis=1)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_rule(self):
        """
        '探尺差'
        探尺 东 南 西 的悬料
        :return:
        """
        res = pd.DataFrame()
        df = get_df('探尺（南）', self.table)
        # 格式化
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])

        # 把三个探尺高度筛选出来
        brothel = ['探尺（南）', '探尺（东）', '探尺（西）']
        hookers = []
        for hooker_name in brothel:
            hooker = df.groupby('采集项名称').get_group(hooker_name).set_index('业务处理时间')  # 筛选
            hooker.drop(columns=['采集项编码', '采集项名称'], inplace=True)
            hooker.rename(columns={'采集项值': hooker_name}, inplace=True)

            hooker[hooker_name][hooker[hooker_name] > 1e7] = None  # 去除1e7 的异常值
            hooker[hooker_name].drop_duplicates(keep=False, inplace=True)  # 去除数据源中同一时刻的重复采样

            # 计算有没有悬料：
            xuan = hooker.sort_index()

            xuan['diff'] = xuan.diff()
            temp = xuan.where(xuan['diff'] == 0).dropna()
            xuan_res = temp.where(temp[hooker_name] > 1.5).dropna()  # 悬料的计算结果

            # xuan_time_table = self.time_table
            # xuan_time_table['next_start'] = xuan_time_table['受铁开始时间'].shift(-1)

            res[hooker_name + '悬料'] = xuan_res.resample('1d').count()[hooker_name]  # 数出日悬料次数

            hookers.append(hooker)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)

        # 找出 所有 在同一时刻 三个探尺高度数据都不缺失的样本
        temp = pd.merge(hookers[0], hookers[1], how="inner", left_index=True, right_index=True)
        blondie = pd.merge(temp, hookers[2], how="inner", left_index=True, right_index=True)
        # 计算极差
        wife = pd.DataFrame()
        wife['探尺差'] = blondie.max(axis=1) - blondie.min(axis=1)

        temp = wife.resample('1d').mean()  # 日重采样
        self.res = pd.merge(self.res, temp, how="outer", left_index=True, right_index=True)

        return res

    def get_wind(self):
        """
        送风风量,热风压力,标准风速,热风温度  {'富氧压力', '富氧量', '风口总面积'}

        实际风速 = 标准风速*(0.101325/273)*((273+风温)/(风压/10+0.101325))

        透气性指数 = 送风风量 / (热风压力 - 炉顶压力1,2) * 100

        压差 = 热风压力 - 炉顶压力

        :return:
        """
        param_list = "富氧压力 富氧量 风口总面积 送风风量 热风压力 标准风速 热风温度".split()
        res = self.process_easy(param_list)

        # 计算区
        res['实际风速'] = res['标准风速'] * (0.101325 / 273) * ((273 + res['热风温度']) / (res['热风压力'] / 1000 + 0.101325))
        # "需要 get_loading() 函数前置！！
        res['透气性指数'] = res['送风风量'] / (res['热风压力'] - self.res['炉顶压力']) * 100  # 需要 get_loading 函数前置
        res['压差'] = res['热风压力'] - self.res['炉顶压力']

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_gas(self):
        """
        炉腹煤气发生量, 炉腹煤气指数
        :return:
        """
        param_list = "炉腹煤气发生量 炉顶煤气CO 炉顶煤气CO2 炉顶煤气H2".split()
        res = self.process_easy(param_list)
        res['炉腹煤气量指数'] = res['炉腹煤气发生量'] / (9.5 * 9.5 * 3.14 / 4)
        res['煤气利用率'] = res['炉顶煤气CO2'] / (res['炉顶煤气CO'] + res['炉顶煤气CO2'])
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_lugang1(self):
        param_list = "理论燃烧温度 鼓风动能".split()
        res = self.process_easy(param_list)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_iron_temp(self):
        """
        [铁水温度]
        :return:
        """
        param_list = "[铁水温度]".split()
        res = self.process_easy(param_list)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

def main():
    solv = Solution(201)
    solv.get_coke()
    solv.get_molten_iron()
    solv.get_deltaTi()
    solv.get_slag()
    solv.get_deltaR2()
    solv.get_ratio()
    solv.get_loading()
    solv.get_wind()
    solv.get_gas()
    solv.get_rule()
    dfs = solv.res
    dfs.to_excel('每日数据2月以后部分指标.xlsx')  # 暂时保存一下


if __name__ == '__main__':
    # 给出 数据批号代码
    print(" ")

    # 下面还有处理异常和缺失
