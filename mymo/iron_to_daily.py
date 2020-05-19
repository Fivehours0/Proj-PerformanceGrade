"""
:describe: 
    可为数据添加受铁开始时间和结束时间
    可将铁次数据转化为每日数据
"""


import pandas as pd
from mymo.get_things import get_df, get_time_table


class IronToDaily:
    def __init__(self, iron_data, table, save_path=None):
        """
        要求iron_data的index为铁次号
        Parameter
        ---------
            iron_data: DataFrame
                铁次化数据。要求index为铁次号
            table: list
                部分数据需要使用源数据进行处理, 需要输入table指标, 输入get_things.get_df函数获取源数据, 例如[19, 20, 201]
            save_path: str
                数据保存地址
        """
        self.iron_data = iron_data.copy()  # 铁次数据，在类函数start中输入
        # 铁次化数据转化为每日数据的参考时间
        self.iron_to_daily_key: str = '受铁结束时间'

        self.table = table
        self.save_path = save_path
        # iron_data中, 将当日的铁次样本求和得当日的每日样本的参数。只需要将参数列出即可, 程序会自动过滤不在iron_data中的参数
        self.sum_list: list = "铁次渣量 40赤块	冶金焦（自产）	南非块矿	小块焦	烧结矿	白马球团	酸性烧结矿	\
                    铁次铁量 探尺（南）悬料   探尺（东）悬料   探尺（西）悬料 ".split()
        # iron_data中, 每日样本无法通过铁次样本获得, 需要从源数据中重采样的参数。只需要将参数列出即可, 程序会自动过滤不在iron_data中的参数
        self.business_list: list = ['日喷煤量']  # 目前只能处理业务时间类型的数据
        # iron_data中, 一些不需要处理的参数数据列。只需要将参数列出即可, 程序会自动过滤不在iron_data中的参数
        self.drop_list: list = ['铁次号', '受铁开始时间', '受铁结束时间', '唐珏老师标签', '系统评分', '现场评分']
        # iron_data中, 将当日的铁次样本求和取平均得当日的每日样本的参数。只需要将参数列出即可, 程序会自动过滤不在iron_data中的参数
        self.mean_list: list = list(set(self.iron_data.keys()) - set(self.sum_list) - set(self.business_list))

        # 输出得每日数据结果保存在res中
        self.res = pd.DataFrame()

    def drop_param_not_in_data_keys(self, param_list: list):
        """
        去除param_list中，不存在于iron_data.keys()中的参数
        :param param_list: list, 参数列表
        :return: list, param_list存在于iron_data.keys()中的参数列表
        """
        param_list_ret = list(set(param_list) & set(self.iron_data.keys()))
        return param_list_ret

    def get_one_param_data(self, param):
        """
            获取某一参数的数据
        """
        if param == '日喷煤量':  # 日喷煤量通过喷吹速率计算得到
            param = '喷吹速率'
        df = get_df(param, self.table)
        data_ret = df.groupby('采集项名称').get_group(param)  # 在数据表中获取param数据

        # 整理数据格式
        data_dict = {param: pd.to_numeric(data_ret['采集项值']), '业务处理时间': pd.to_datetime(data_ret['业务处理时间'])}
        data_ret = pd.DataFrame(data_dict)

        data_ret.where(data_ret[param] < 1e7, inplace=True)  # 去除异常值
        data_ret = data_ret.set_index('业务处理时间')
        return data_ret

    def get_iron_time(self):
        """
            获取铁次时间表
        """
        return get_time_table(self.table)

    def add_date(self):
        """
            去掉self.iron_to_daily_key(受铁开始时间或者受铁结束时间)的时分秒, 添加到data中, 用以聚合, 最后会删除

            即将self.iron_to_daily_key作为铁次转化为每日的时间参考
        """
        iron_time = self.get_iron_time()[self.iron_to_daily_key]
        iron_time = pd.to_datetime(iron_time).dt.floor('d').rename('日期')
        self.iron_data = pd.merge(self.iron_data, iron_time, how='left', left_index=True, right_index=True)
        return self.iron_data

    def drop_useless_data(self):
        """
            丢弃一些不需要处理的参数
        """
        # iron_data中, 不需要处理, 将其丢弃的的参数
        for value in self.drop_list:
            if value in self.iron_data.keys():
                self.iron_data.drop(value, axis=1, inplace=True)

    def business_time_deal(self):
        """
            每日样本无法通过铁次样本获得, 需要从源数据中重采样的参数。该函数只能处理业务处理时间类型的数据。
        """
        # 去除self.special_list中，不存在于iron_data.keys()中的参数
        business_list = self.drop_param_not_in_data_keys(self.business_list)

        res = pd.DataFrame()
        for param in business_list:
            one_param_data = self.get_one_param_data(param)
            one_param_data = one_param_data.resample('1D').mean()
            res = pd.merge(res, one_param_data, how='outer', left_index=True, right_index=True)

        if '日喷煤量' in business_list:
            res['日喷煤量'] = res['喷吹速率'] * 24 * 60  # 每分钟喷煤量 * 24小时 * 60分钟

        self.res = pd.merge(self.res, res[business_list], how='left', left_index=True, right_index=True)

    def sum_deal(self):
        """
            处理 将当天的铁次样本数据求和得到天样本数据 这种类型的指标
        """
        # 去除self.sum_list中，不存在于iron_data.keys()中的参数
        sum_list = self.drop_param_not_in_data_keys(self.sum_list)
        sum_list.append('日期')
        res = self.iron_data[sum_list].groupby('日期').sum()
        self.res = pd.merge(self.res, res, how='outer', left_index=True, right_index=True)

    def mean_deal(self):
        """
            处理 将当天的铁次样本数据求和取平均得到天样本数据 这种类型的指标
        """
        # 去除mean_list中，不存在于iron_data.keys()中的参数
        mean_list: list = self.drop_param_not_in_data_keys(self.mean_list)

        mean_list.append('日期')
        res = self.iron_data[mean_list].groupby('日期').mean()
        self.res = pd.merge(self.res, res, how='outer', left_index=True, right_index=True)

    def save_data(self):
        """
            保存数据
        """
        if self.save_path is not None:
            self.res.to_excel(self.save_path)

    def start(self):

        self.add_date()  # 为data添加一列日期(格式: 年月日)数据, 用以聚合
        self.drop_useless_data()  # 丢弃一些不需要处理的参数
        self.sum_deal()  # 处理 将当天的铁次样本数据求和得到天样本数据 这种类型的指标
        self.mean_deal()  # 处理 将当天的铁次样本数据求和取平均得到天样本数据 这种类型的指标
        self.business_time_deal()  # 要放在sum_deal和mean_deal之后处理, 因为该函数使用的是源数据, 会带入一部分先前被异常处理掉的数据

        self.save_data()


def main():
    import os

    os.chdir('../')
    print(os.getcwd())

    data_path = 'data/铁次252plus_201_v3.5.xlsx'
    save_path = 'data/每日252plus_v1.0.xlsx'

    table = 201
    iron_data = pd.read_excel(data_path)

    iron_to_daily = IronToDaily(iron_data, table=table, save_path=save_path)

    iron_to_daily.start()


if __name__ == "__main__":
    main()
