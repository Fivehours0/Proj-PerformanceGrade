"""
create time : 2020-04-13 22:57:00
author: xsz
version: alpha
description:

目标：进行 100每日指标整理

"""
import numpy as np
import pandas as pd
from mymo.get_things import get_df
from matplotlib import pyplot as plt

class Solution:
    def __init__(self, input_table):
        self.table = input_table

    def get_df_format(self, input_param):
        """
        获取指标含有指标数据表时 处理好格式
        :param input_table:
        :param input_param:
        :return:
        """
        df_ = get_df(input_param,  self.table)
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

    def get_coke(self):
        """
        计算焦炭5个性能参数日均值
        数据源A 本身就归好了日期, 进行groupby操作即可
        """
        res = pd.DataFrame()
        param_list = [
            '焦炭粒度、冷强度_M40',
            '焦炭粒度、冷强度_M10',
            '焦炭工分_St',
            '焦炭热性能_CRI',
            '焦炭热性能_CSR']
        param_list_id = [34, 35, 38, 36, 37]
        df = self.get_df_format(param_list[0])
        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param)
            temp1 = temp.groupby('业务处理时间').mean()
            res[param] = temp1['采集项值'].copy()
        return res

    def get_molten_iron(self):
        param_list = ['[C]', '[Ti]', '[Si]', '[S]']
        res = pd.DataFrame()
        df = self.get_df_format(param_list[0])
        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param)
            temp1 = temp.groupby('业务处理时间').mean()
            res[param] = temp1['采集项值'].copy()
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
        return res

    def get_delta_R2(self):
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

        res['日喷煤量'] = df2.groupby('业务处理时间').mean()['采集项值']  # 先求每日的均值
        res['日喷煤量'] = res['日喷煤量'] * 24 * 60  # 每分钟喷煤量 * 24小时 * 60分钟
        # temp = df.groupby('业务处理时间').apply(np.max)
        res['煤比'] = res['日喷煤量'] / res['日产量'] * 20

        res['燃料比'] = res['焦比'] + res['煤比']
        return res


if __name__ == '__main__':
    # 给出 数据批号代码
    solv = Solution(201)
    res0 = []
    res0.append(solv.get_coke())
    res0.append(solv.get_molten_iron())
    res0.append(solv.get_deltaTi())
    res0.append(solv.get_slag())
    res0.append(solv.get_delta_R2())
    res0.append(solv.get_ratio())
    dfs = pd.concat(res0, axis=1)
    # dfs.to_excel('每日数据2月以后部分指标.xlsx') # 暂时保存一下

    # 下面还有处理异常和缺失
