"""
:describe: 
    可为数据添加受铁开始时间和结束时间
    可将铁次数据转化为每日数据
"""

import numpy as np
import pandas as pd
import os
from get_things import get_df, get_time_table

class IronToDaily:
    def __init__(self, iron_data, table=None, sum_list=None, drop_list=None, special_list=None, 
                 score=None, save=False, save_path=None):
        """
        Parameter
        ---------
            iron_data: DataFrame
                index为铁次号, 包含有受铁开始, 结束时间列, 以及其他指标, 参数数据列
            table: list
                部分数据需要使用源数据进行处理, 需要输入table指标, 输入get_things.get_df函数获取源数据, 例如[19, 20, 201]
            sum_list: list
                iron_data中, 将当日的铁次样本求和的当日的每日样本的参数
            drop_list: list
                iron_data中, 不需要处理, 将其丢弃的的参数
            special_list: list
                iron_data中, 每日样本无法通过铁次样本获得, 需要从源数据中重采样得参数
            score: DataFrame
                index为日期, 年月日格式, 数据列为系统评分和现场评分
            save: bool
                是否保存数据
            save_path: str
                数据保存地址
        """
        self.iron_data = iron_data
        self.table = table
        self.sum_list = sum_list
        self.drop_list = drop_list
        self.special_list = special_list
        self.score = score
        self.save = save
        self.save_path = save_path
        # 输出得每日数据结果保存在res中
        self.res = pd.DataFrame()

    def get_one_param_all_batch_data(self, param):
        '''
            获取某一参数的所有批数据
        '''
        all_batch_data_list = [] # 所有批次的数据先保存在列表中, 之后使用concat合并
        all_batch_data = pd.DataFrame() # 保存使用concat合并后的数据
        if param == '日喷煤量': # 日喷煤量通过喷吹速率计算得到
            param = '喷吹速率'
        for table in self.table:
            df = get_df(param, table)
            df['采集项值'] = pd.to_numeric(df['采集项值'])
            df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
            df.where(df['采集项值'] < 1e7, inplace=True)
            one_param_data = df.groupby('采集项名称').get_group(param).set_index('业务处理时间')['采集项值']
            all_batch_data_list.append(one_param_data)
        all_batch_data = pd.concat(all_batch_data_list).to_frame(name=param)
        return all_batch_data

    def add_iron_time(self):
        '''
            为数据添加受铁开始时间和结束时间
        '''
        if '受铁结束时间' not in self.iron_data.keys():
            try:
                if self.table is None:
                    raise ValueError("ERROR: " + str(os.path.basename(__file__)) + "数据中不包含受铁时间数据,请输入table参数")
                all_batch_time_list = [] # 保存不同批次的铁次时间
                all_batch_time = pd.DataFrame() # 所有保存在all_batch_time_list中的铁次时间数据合并
                for table in self.table:
                    all_batch_time_list.append(get_time_table(table))
                all_batch_time = pd.concat(all_batch_time_list)
                # 添加受铁开始时间和结束时间
                self.iron_data = pd.merge(self.iron_data, all_batch_time, how='left', left_index=True, right_index=True)
                return self.iron_data
            except ValueError as v:
                print(v)
                os._exit(0)

    def add_date(self, ironTime=None):
        '''
        去掉ironTime(受铁开始时间或者受铁结束时间)的时分秒, 添加到data中, 用以添加评分, 最后会删除
        因为评分表是以日期为参照的, 所以需要添加该列作为对照

        Parameters
        ----------
            ironTime: 铁次时间数据, 传入受铁开始时间或者受铁结束时间 类型: Series, index为铁次号
        '''

        ironTime = pd.to_datetime(ironTime).dt.floor('d').rename('日期')
        self.iron_data = pd.merge(self.iron_data, ironTime, how='left', left_index=True, right_index=True)
        return self.iron_data

    def drop_useless_data(self):
        '''
            丢弃一些不需要处理的参数
        '''
        # iron_data中, 不需要处理, 将其丢弃的的参数
        drop_list = ['铁次号', '受铁开始时间', '受铁结束时间', '唐珏老师标签', '系统评分', '现场评分'] 
        if self.drop_list is not None:
            drop_list += self.drop_list
        for value in drop_list:
            if value in self.iron_data.keys():
                self.iron_data.drop(value, axis=1, inplace=True)

    def specail_deal(self):
        """
            每日样本无法通过铁次样本获得, 需要从源数据中重采样的参数
        """
        if self.special_list is not None:
            res = pd.DataFrame()
            for param in self.special_list:
                all_batch_data = self.get_one_param_all_batch_data(param)
                all_batch_data = all_batch_data.resample('1D').mean()
                res = pd.merge(res, all_batch_data, how='outer', left_index=True, right_index=True)

            res['日喷煤量'] = res['喷吹速率'] * 24 * 60  # 每分钟喷煤量 * 24小时 * 60分钟

            self.res = pd.merge(self.res, res[self.special_list], how='left', left_index=True, right_index=True)

    def sum_deal(self):
        """
            处理 将当天的铁次样本数据求和得到天样本数据 这种类型的指标
        """
        if self.sum_list is not None:
            res = pd.DataFrame()
            self.sum_list.append('日期') 
            res = self.iron_data[self.sum_list].groupby('日期').sum()
            self.res = pd.merge(self.res, res, how='outer', left_index=True, right_index=True)

    def mean_deal(self):
        """
            处理 将当天的铁次样本数据求和取平均得到天样本数据 这种类型的指标
        """
        # iron_data中, 将当日的铁次样本求和取平均得当日的每日样本的参数
        sum_list = set() if self.sum_list is None else set(self.sum_list)
        special_list = set() if self.special_list is None else set(self.special_list)
        mean_list = list(set(self.iron_data.keys()) - sum_list - special_list)
        if mean_list is not None:
            res = pd.DataFrame()
            mean_list.append('日期')
            res = self.iron_data[mean_list].groupby('日期').mean()
            self.res = pd.merge(self.res, res, how='outer', left_index=True, right_index=True)

    def saveData(self):
        '''
        保存数据

        Parameters
        ----------
            save: 是否保存数据 类型: boolean
            savePath: 保存地址 类型: str
        '''        
        if self.save == True:
            try:
                if self.save_path is None:
                    raise ValueError("未设置")
                self.res.to_excel(self.save_path)
            except ValueError as v:
                print(v)
                os._exit(0)

    def start(self):
        self.add_iron_time()
        self.add_date(self.iron_data['受铁结束时间']) # 为data添加一列日期(格式: 年月日)数据, 用以聚合
        self.drop_useless_data() # 丢弃一些不需要处理的参数
        self.sum_deal()
        self.mean_deal()
        self.specail_deal() # 要放在sum_deal和mean_deal之后处理, 因为该函数使用的是源数据, 会带入一部分先前被异常处理掉的数据

        # 添加分数, 分数的日期格式也为年月日, 可以直接进行合并
        if self.score is not None:
            self.iron_data = pd.merge(self.iron_data, self.score, how='left', left_index=True, right_index=True)

        self.saveData()
        
def main():
    data_path = 'data/铁次252plus_v3.5.xlsx'
    save_path = 'data/每日252plus_v1.0.xlsx'
    score_path = 'data/分数.xlsx'
    # 数据中不包含受铁结束时间和受铁开始时间时也需要键入table
    # 部分数据需要使用源数据进行处理, 需要输入table指标, 输入get_things.get_df函数获取源数据
    table = [19, 20, 201]

    # iron_data中, 将当日的铁次样本求和得当日的每日样本的参数
    sum_list = "铁次渣量 40赤块	冶金焦（自产）	南非块矿	小块焦	烧结矿	白马球团	酸性烧结矿	\
                铁次铁量 探尺（南）悬料   探尺（东）悬料   探尺（西）悬料 ".split()
 
    # iron_data中, 每日样本无法通过铁次样本获得, 需要从源数据中重采样的参数
    special_list = ['日喷煤量'] 

    iron_data = pd.read_excel(data_path)
    score = pd.read_excel(score_path).set_index('日期')

    ironToDaily = IronToDaily(iron_data, table=table, sum_list=sum_list, drop_list=None, special_list=special_list,
                              score=score, save=True, save_path=save_path)

    ironToDaily.start()

if __name__ == "__main__":
    main()