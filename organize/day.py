"""
create time : 2020-4-16
author: xsz
version: v4
description:

目标：进行 100每日指标整理

依赖： 三批数据源的pkl文件， 名称罗列表

"""
import numpy as np
import pandas as pd
from organize.env import get_df
from organize.env import find_table
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
            try:
                temp = df.groupby('采集项名称').get_group(param)
            except KeyError:
                table_path = find_table(param_list[0], self.table)
                print("警告！ 数据批次代码为", self.table, "的表: ", table_path, ", 无指标" + param + "的任何数据")
                res[param] = np.nan
            else:
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
            # df_['业务处理时间'] = df_['业务处理时间'].apply(pd.to_datetime)
            df_['业务处理时间'] = pd.to_datetime(df_['业务处理时间'])
            df_['业务处理时间'] = df_['业务处理时间'].dt.floor('d')  # 时间对天取整数
        if '采集项值' in df_.columns:
            # df_['采集项值'] = df_['采集项值'].apply(pd.to_numeric) 此代码处理费时
            df_['采集项值'] = pd.to_numeric(df_['采集项值'])
            # 在这进行 去除999的操作
            # df_['采集项值'][df_['采集项值'] > 1e7] = np.nan
            df_['采集项值'].where(df_['采集项值'] < 1e7, inplace=True)

        if '铁次号' in df_.columns and df_['铁次号'][0] != ' ':
            df_['铁次号'] = pd.to_numeric(df_['铁次号'])  # 速度提升

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
        # df2['采集项值'][df2['采集项值'] > 1e7] = np.nan
        df2['采集项值'].where(df2['采集项值'] < 1e7, inplace=True)

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
        param_list = ["[铁水温度]"]
        res = self.process_easy(param_list)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_iron_count(self):
        """
        日出铁次数  出铁次数/出铁时间
        需要 铁次时间表
        :return:
        """
        res = pd.DataFrame()
        path = 'data/西昌2#高炉数据20年2-4月/铁次时间.xlsx'
        df_tb = pd.read_excel(path)
        df_tb['受铁结束时间'] = pd.to_datetime(df_tb['受铁结束时间'])  # 格式化
        df_tb['受铁开始时间'] = pd.to_datetime(df_tb['受铁开始时间'])  # 格式化

        temp = df_tb.set_index('受铁开始时间')['铁次号']
        res['日出铁次数'] = temp.resample('1d').count()

        # 出铁时间
        df_tb['time_len'] = (df_tb['受铁结束时间'] - df_tb['受铁开始时间']) / pd.to_timedelta('1min')  # 单位分钟
        # 对天进行重采样计算一天的累计受铁时间
        temp = df_tb.set_index('受铁开始时间')['time_len']
        res['出铁次数/出铁时间'] = res['日出铁次数'] / temp.resample('1d').sum()

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def process_range(self, param_list, agg_func=np.mean):
        """
        处理极差指标
        :param param_list 指标集合，必须在同一个excel文件中
        :param table 表的代码
        :param agg_func 聚合函数 默认取平均
        """
        res = pd.DataFrame()
        df = self.get_df_format(param_list[0])

        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param)
            temp_max = temp.groupby('业务处理时间').max()
            temp_min = temp.groupby('业务处理时间').min()
            res[param] = (temp_max['采集项值'] - temp_min['采集项值']).copy()
        return res

    def get_furnace_temp(self):
        """
        炉温相关指标的一般处理和极差处理
        '炉喉温度极差', '炉顶温度极差'
        '炉顶温度', '炉喉温度', '炉腰温度', '炉身下二段温度',
        :return:
        """
        all_temp_param = [['炉顶温度1', '炉顶温度2', '炉顶温度3', '炉顶温度4',
                           '炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6', '炉喉温度7', '炉喉温度8'],
                          ['炉腰温度1', '炉腰温度2', '炉腰温度3', '炉腰温度4', '炉腰温度5', '炉腰温度6',
                           '炉身下一层温度1', '炉身下一层温度2', '炉身下一层温度3', '炉身下一层温度4',
                           '炉身下一层温度5', '炉身下一层温度6', '炉身下一层温度7', '炉身下一层温度8',
                           '炉身下二层温度1', '炉身下二层温度2', '炉身下二层温度3', '炉身下二层温度4',
                           '炉身下二层温度5', '炉身下二层温度6', '炉身下二层温度7', '炉身下二层温度8'],
                          ['炉缸温度1', '炉缸温度2', '炉缸温度3', '炉缸温度4', '炉缸温度5', '炉缸温度6',
                           '炉底温度1', '炉底温度2', '炉底温度3', '炉底温度4', '炉底温度5', '炉底温度6', '炉缸中心温度']]
        res = pd.DataFrame()
        for param_list in all_temp_param:
            tmp_res = self.process_easy(param_list)
            res = pd.merge(res, tmp_res, how="outer", left_index=True, right_index=True)

        res['炉顶温度'] = res[['炉顶温度1', '炉顶温度2', '炉顶温度3', '炉顶温度4']].mean(axis=1)
        res['炉喉温度'] = res[['炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6',
                           '炉喉温度7', '炉喉温度8']].mean(axis=1)
        res['炉喉温度'] = res[['炉腰温度1', '炉腰温度2', '炉腰温度3', '炉腰温度4', '炉腰温度5', '炉腰温度6']].mean(axis=1)
        res['炉身下二段温度'] = res[['炉身下二层温度1', '炉身下二层温度2', '炉身下二层温度3', '炉身下二层温度4',
                              '炉身下二层温度5', '炉身下二层温度6', '炉身下二层温度7', '炉身下二层温度8']].mean(axis=1)

        # 以下为极差指标处理
        res_temp = pd.DataFrame()
        range_param_list = ['炉顶温度1', '炉顶温度2', '炉顶温度3', '炉顶温度4']
        res_temp = self.process_range(range_param_list)
        res['炉顶温度极差'] = res_temp.mean(axis=1)

        range_param_list = ['炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6', '炉喉温度7', '炉喉温度8']
        res_temp = self.process_range(range_param_list)
        res['炉喉温度极差'] = res_temp.mean(axis=1)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res


"""
    # 没有 冶金焦（自产） 对应的 冶金焦综合样_CaO 的CaO含量
    # def get_zha(self):
    #     
    #     #计算日渣量
    #     #每日渣量:
    #     #[40赤块_CaO*40赤块+冶金焦综合样_CaO*冶金焦（自产）+南非块矿_CaO*南非块矿+小块焦_CaO*小块焦+
    #     #烧结矿成分_CaO*烧结矿+白马球团_CaO*白马球团+酸性烧结矿_CaO*酸性烧结矿]/(CaO)
    #
    #     #渣铁比,kg/t = 每日渣量 / 日产量
    #     #:return:
    #     
    #
    #     list1 = "40赤块_CaO 冶金焦综合样_CaO 南非块矿_CaO " \
    #             "小块焦_CaO 烧结矿成分_CaO    白马球团_CaO 酸性烧结矿_CaO".split()
    #     res = self.process_easy(list1)
    #
    #     param_list = "40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()
    #     df_coke = self.process_easy(param_list, np.sum)
    #
    #     res.fillna(0, inplace=True)
    #     df_coke.fillna(0, inplace=True)
    #
    #     res['每日渣量'] = 0
    #     for i in range(7):
    #         res['每日渣量'] = res['每日渣量'] + res.iloc[:, i] * df_coke.iloc[:, i]
    #     res['每日渣量'] = res['每日渣量'] / self.res['(CaO)']  # 问题: 铁次区间没有 加矿呢???
    #     res['渣铁比'] = res['每日渣量'] / self.res['日产量']
    #     self.res = pd.merge(res.loc[:, ['每日渣量', '渣铁比']], self.res, how="outer", left_index=True,
    #                         right_index=True)
    #     return res
"""


def main(table_id):
    solv = Solution(table_id)
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
    solv.get_lugang1()
    solv.get_iron_count()
    solv.get_furnace_temp()
    dfs = solv.res
    # dfs.apply(lambda x: x.fillna(x.mean(), inplace=True))  # 缺失值均值填充
    dfs.to_excel('organize/cache/每日.xlsx')
    return None


def test():
    """
    代码测试区域
    :return:
    """
    self = Solution(201)
    # params = ['炉缸温度1', '炉缸温度2', '炉缸温度3', '炉缸温度4', '炉缸温度5', '炉缸温度6',
    #           '炉底温度1', '炉底温度2', '炉底温度3', '炉底温度4', '炉底温度5', '炉底温度6', '炉缸中心温度']
    # params = ['炉缸温度1', '炉缸温度2']
    # tmp_res = self.process_easy(params)
    self.get_furnace_temp()
    self.res.to_excel('测试每日温度输出v1.0.xlsx')
    print("work done!")
    # return tmp_res


# if __name__ == '__main__':
#     # 给出 数据批号代码
#     print(" ")
#
#     # 下面还有处理异常和缺失
