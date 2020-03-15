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
PRE_PATH = {19: 'data/西昌2#高炉数据19年10-11月/pkl/',
            20: 'data/西昌2#高炉数据19年12月-20年2月/pkl/'}
# 铁次时间表的存放路径
IRON_TIME = {19: 'data/西昌2#高炉数据19年10-11月/铁次时间.xlsx',
             20: 'data/西昌2#高炉数据19年12月-20年2月/origin/铁次时间.xlsx'}


def find_table(name, table):
    """
    给出指标 自动寻找在那个表里
    :param name: 要寻找的指标名
    :param table 数据源选择 取值 19 或者 20
    :return 表名
    """
    if table == 19:
        path = 'data/19数据表各个名称罗列.xlsx'
    elif table == 20:
        path = 'data/20数据表各个名称罗列.xlsx'
    dic = pd.read_excel(path)
    temp = dic[dic.isin([name])].dropna(axis=1, how='all')
    if temp.values.shape[1] == 0:
        print("表:", table, "无", name, "!!!!")
        return None
    elif temp.values.shape[1] == 1:
        return temp.columns[0]
    elif temp.values.shape[1] > 1:
        print("表:", table, "有大于一个的", name, "自动返回发现的第一个")
        return temp.columns[0]


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
        # time = df['业务处理时间']  # 注意 temp 与 df['业务处理时间'] 一个地址
        df.set_index('业务处理时间', inplace=True)
        for i in range(self.time_table.shape[0]):
            start, end = self.time_table['受铁开始时间'].iloc[i], self.time_table['受铁结束时间'].iloc[i]
            df.loc[start:end, '铁次号'] = self.time_table.index[i]
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
        # df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])  # 格式化
        df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化
        df = df[df['铁次号'] >= 20000000]  # 提取出#2高炉的数据
        df = df[df['铁次号'] < 30000000]

        # 这里假设 param_list 中的指标都在一个表里
        for param in param_list:
            if not any(df["采集项名称"].isin([param])):
                raise KeyError("df 中 没有 param", df.shape, param)
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

    def get_ratio(self, five_lag=False):
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
        df_coke = self.time2order(df_coke, five_lag=five_lag)
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

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)

        return res

    def get_gas(self):
        """
        炉腹煤气发生量, 炉腹煤气指数
        :return:
        """
        res = self.process_big_time('炉腹煤气发生量')
        res['炉腹煤气量指数'] = res['炉腹煤气发生量'] / (9.5 * 9.5 * 3.14 / 4)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def process_chemical(self, list2, df, five_lag=False):
        """
        数据特点, 没有 业务处理时间 有上料批次号 处理料的化验
        焦炭热性能_CSR 这玩意 一天一采集, 必须以数据为模板
        """

        def to_time(x):
            """
            cost many time
            191013D000402-2401 处理成 2019-10-14 00:01:00 提供apply 使用
            """
            if x[-4:-2] != '24':
                return pd.to_datetime('20' + x[0:6] + x[-4:])
            else:
                return pd.to_datetime('20' + x[0:6] + '00' + x[-2:]) + pd.to_timedelta('1D')

        list3 = list2[0::2]
        list1 = list2[1::2]

        # 指标在表中有没有呀?
        param_path = [find_table(list1[i], self.table) for i in range(len(list1))]

        # df['业务处理时间'] = df['上料批号'].apply(to_time)
        df['采集项值'] = df['采集项值'].apply(pd.to_numeric)
        res = pd.DataFrame()
        for i, item in enumerate(param_path):
            param = list3[i]
            group_name = list1[i]
            if item is not None:
                # 需要对 检化验数据 写单独的处理函数
                df_grouped = df.groupby("采集项名称").get_group(group_name)
                df_grouped['业务处理时间'] = df_grouped['上料批号'].apply(to_time)  # 应该确保上料批次号符合这样的格式: 191013xxxxxxx-2401

                if five_lag:  # 如果需要滞后
                    df_grouped['业务处理时间'] = df_grouped['业务处理时间'] - pd.to_timedelta('5h')

                df_grouped.set_index('业务处理时间', inplace=True)
                df_rsp = df_grouped.resample('1T').mean().ffill()
                res[param] = self.time_table.apply(lambda x: df_rsp.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                                   axis=1)
                res[param] = res[param].ffill()
            else:
                res[param] = None

        return res

    def get_chemical(self, five_lag=False):
        """
        数据特点, 没有 业务处理时间 有上料批次号
        焦炭热性能_CSR 这玩意 一天一采集, 必须以数据为模板
        """
        list2 = "M40 焦炭粒度、冷强度_M40 \
        M10 焦炭粒度、冷强度_M10 \
        CRI 焦炭热性能_CRI \
        CSR 焦炭热性能_CSR \
        St 焦炭工分_St \
        Ad 焦炭工分_Ad \
        Mt 焦炭水分_Mt \
        喷吹煤Ad,%  喷吹煤粉_Ad \
        喷吹煤St，%  喷吹煤粉_St \
        喷吹煤Vd，%  喷吹煤粉_Vdaf \
        烧结矿转鼓强度,% 烧结矿性能样(粒度、强度)_转鼓指数".split()
        # df = pd.concat([self.get_df('焦炭粒度、冷强度_M40'), self.get_df('白马球团_Zn')])
        df = self.get_df('焦炭粒度、冷强度_M40')
        res = self.process_chemical(list2, df, five_lag)
        self.res = pd.merge(res, self.res, how="outer", left_index=True, right_index=True)
        return res

    def get_slag_amount(self, five_lag=False):
        """
        铁次渣量:
        [40赤块_CaO*40赤块+冶金焦综合样_CaO*冶金焦（自产）+南非块矿_CaO*南非块矿+小块焦_CaO*小块焦+
        烧结矿成分_CaO*烧结矿+白马球团_CaO*白马球团+酸性烧结矿_CaO*酸性烧结矿]/(CaO)

        渣铁比,kg/t = 铁次渣量 / 铁次铁量
        :return:
        """
        res = pd.DataFrame()
        list1 = "40赤块_CaO 40赤块_CaO 冶金焦综合样_CaO 冶金焦综合样_CaO 南非块矿_CaO 南非块矿_CaO " \
                "小块焦_CaO 小块焦_CaO 烧结矿成分_CaO 烧结矿成分_CaO 白马球团_CaO 白马球团_CaO 酸性烧结矿_CaO 酸性烧结矿_CaO".split()
        df = self.get_df(list1[0])

        res = self.process_chemical(list1, df, five_lag)
        # df1.merge(df2, how='left')

        param_list = "40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()
        param = param_list[0]
        df_coke = self.get_df(param)
        df_coke = self.time2order(df_coke, five_lag=five_lag)
        df_coke = self.process_iron(df_coke, param_list, np.sum)
        # res['焦比'] = (df_coke['冶金焦（自产）'] + df_coke['小块焦'])
        res.fillna(0, inplace=True)
        df_coke.fillna(0, inplace=True)
        res['铁次渣量'] = 0
        for i in range(7):
            res['铁次渣量'] = res['铁次渣量'] + res.iloc[:, i] * df_coke.iloc[:, i]
        res['铁次渣量'] = res['铁次渣量'] / self.res['(CaO)']  # 问题: 铁次区间没有 加矿呢???
        res['铁次渣量 / 铁次铁量'] = res['铁次渣量'] / self.res['铁次铁量']
        self.res = pd.merge(res.loc[:, ['铁次渣量', '铁次渣量 / 铁次铁量']], self.res, how="outer", left_index=True,
                            right_index=True)
        return res

    def get_rule(self, five_lag=False):
        """
        # 计算探尺差
        # 探尺差
        # 西昌2#高炉采集数据表_上料系统
        """
        if self.table == 20:
            path = 'data/西昌2#高炉数据19年12月-20年2月/pkl/西昌2#高炉采集数据表_上料系统.pkl'
        elif self.table == 19:
            path = 'data/西昌2#高炉数据19年10-11月/pkl/西昌2#高炉采集数据表_上料系统.pkl'
        df = pd.read_pickle(path)  # 导入

        # 格式化
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        if five_lag:  # 如果需要滞后
            df['业务处理时间'] = df['业务处理时间'] - pd.to_timedelta('5h')

        # 把三个探尺高度筛选出来
        brothel = ['探尺（南）', '探尺（东）', '探尺（西）']
        hookers = []
        for hooker_name in brothel:
            hooker = df.groupby('采集项名称').get_group(hooker_name).set_index('业务处理时间')  # 筛选
            hooker.drop(columns=['采集项编码', '采集项名称'], inplace=True)
            hooker.rename(columns={'采集项值': hooker_name}, inplace=True)

            hooker[hooker_name][hooker[hooker_name] > 1e7] = None  # 去除1e7 的异常值
            hooker[hooker_name].drop_duplicates(keep=False, inplace=True)  # 去除数据源中同一时刻的重复采样
            hookers.append(hooker)

        # 找出 所有 在同一时刻 三个探尺高度数据都不缺失的样本
        temp = pd.merge(hookers[0], hookers[1], how="inner", left_index=True, right_index=True)
        blondie = pd.merge(temp, hookers[2], how="inner", left_index=True, right_index=True)
        # 计算极差
        wife = pd.DataFrame()
        wife['采集项值'] = blondie.max(axis=1) - blondie.min(axis=1)

        self.res['探尺差'] = self.time_table.apply(lambda x: wife.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                                axis=1)

        return self.res['探尺差']


def main(five_lag=False):

    obj19 = Solution(19)
    obj20 = Solution(20)
    objs = [obj19, obj20]

    for obj in objs:  # 对每个数据对象循环
        obj.get_molten_iron()
        obj.get_slag()
        obj.get_wind()
        obj.get_gas()
        obj.get_ratio(five_lag)
        obj.get_chemical(five_lag)
        obj.get_rule(five_lag)
        obj.get_slag_amount(five_lag)

    ans = pd.concat([obj19.res, obj20.res])
    ans[ans == np.inf] = np.nan  # 因为有些铁次铁量为0 从而导致一些煤比 焦比等铁量衍生指标 算出 inf, np.nan填充
    if not five_lag:
        ans.to_excel("data/铁次结果_无滞后处理.xlsx")  # 因为铁次产量为0 搞出不少 inf
    else:
        ans.to_excel("data/铁次结果_5h滞后处理.xlsx")  # 因为铁次产量为0 搞出不少 inf
    return ans


if __name__ == "__main__":
    # ans = main(five_lag=False)
    ans_lag = main(five_lag=True)

    # self = Solution(20)
