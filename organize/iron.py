"""
:describe 按照铁次整理数据
:author 夏尚梓 auxiliary 杜智辉
:version v3.4.2020042520

力图可以把 三个化验表的指标全部整理进去 new bug: 高炉沟参数太多重的

注意：
1. 进来新数据时需要 运行MakePickle.py 转成pkl文件，
2. 运行ShowIndex.py 整理出指标excel对照表。不过，新数据可以直接使用 'data/20数据表各个名称罗列.xlsx'

"""
import numpy as np
import pandas as pd
from organize.env import find_table
from organize.env import get_df
from organize.env import get_time_table
from organize.env import get_iron_speed

CHEMICAL_TABLE_NAME = '西昌2#高炉-上料质量表'  # 处理上料质量表的表名字
SLAG_TABLE_NAME = '西昌2#高炉-上料成分表'  # 处理上料成分表的表名字

ORGANIZE_CONFIG_XLSX = 'organize/config/20数据表各个名称罗列.xlsx'  # 处理上料成分表的所有指标的 依照表的文件


def process_iron(df, param_list, agg_func):
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


def adaptive(param_list_loading):
    """
    对输入的param_list进行适配 以适合被process_chemical调用

    例子：
        ['40赤块_CaO', '冶金焦综合样_CaO']
        --->
        ['40赤块_CaO', '40赤块_CaO','冶金焦综合样_CaO','冶金焦综合样_CaO']

    :param param_list_loading:
    :return:
    """
    # 适配 process_chemical 函数
    temp = []
    for i in param_list_loading:
        temp.append(i)
        temp.append(i)
    return temp


class Solution:
    def __init__(self, table, five_lag=True):
        """
        初始化
        :param table: 数据源选择 取值 19 或者 20
        """
        self.five_lag = five_lag  # 设定滞后统一处理成5hour滞后
        self.table = table  # 处理数据的批次号
        self.res = pd.DataFrame()  # 结果初始化
        self.time_table = self.get_time_table()  # 获取铁次时间表

    def get_time_table(self):
        return get_time_table(self.table)

    def time2order(self, df):
        """
        :param df: 要生成铁次号的 DataFrame
        :return: 添加了 铁次号的 DataFrame
        """
        df['业务处理时间'] = df['业务处理时间'].astype('datetime64')
        df.sort_values('业务处理时间', inplace=True)

        df['铁次号'] = 0
        if self.five_lag:
            df['业务处理时间'] = df['业务处理时间'] - pd.to_timedelta('5h')
        # time = df['业务处理时间']  # 注意 temp 与 df['业务处理时间'] 一个地址
        df.set_index('业务处理时间', inplace=True)
        for i in range(self.time_table.shape[0]):
            start, end = self.time_table['受铁开始时间'].iloc[i], self.time_table['受铁结束时间'].iloc[i]
            df.loc[start:end, '铁次号'] = self.time_table.index[i]
        return df

    def process_business_time(self, df, param_list, range_=False, agg_func=np.mean, resample_=False):
        """
        对业务处理时间型数据 预处理
        读入数据 -> 铁次时间标定 -> 处理 -> 输出
        :param df: 要传入的表
        :param param_list: 要处理的指标列表 类型: list
        :param range_: 是否处理极差数据 类型: bool
        :param agg_func: 聚合方式 类型: 函数, 例如np.mean
        :param resample_: 是否对该参数数据进行重采样 类型: bool
        :return:
        """
        res = pd.DataFrame()
        for param in param_list:
            if not any(df["采集项名称"].isin([param])):
                raise KeyError("df 中 没有 param", df.shape, param)
            df_pure = df.groupby("采集项名称").get_group(param).rename(columns={'采集项值': param})[
                [param, '业务处理时间']]  # 筛选 都在同一个表里
            df_pure[param] = pd.to_numeric(df_pure[param])
            if resample_:
                df_pure['业务处理时间'] = pd.to_datetime(df_pure['业务处理时间'])
                df_pure = df_pure.resample('1min', on='业务处理时间').mean().ffill()
                df_pure = df_pure.reset_index()
            df_pure = self.time2order(df_pure)[[param, '铁次号']][
                df_pure['铁次号'] != 0]  # 将样本用铁次进行标定，删除不在铁次内的数据
            df_pure[param].where(df_pure[param] < 1e6, np.nan, inplace=True)  # 去除 999999 的异常值
            if not range_:
                df_pure = df_pure[param].groupby(df_pure['铁次号']).agg(agg_func)
                nan_iron_order = set(self.time_table.index) - set(df_pure.index)  # 部分铁次号没有数据导致结果中部分铁次缺失，这里把缺失的补上
                df_pure = df_pure.append(pd.Series(np.nan, nan_iron_order)).sort_index().rename(index=param)
            else:
                df_pure_max = df_pure[param].groupby(df_pure['铁次号']).max()  # 得出每个铁次号中值的最大值
                df_pure_min = df_pure[param].groupby(df_pure['铁次号']).min()  # 得出每个铁次号中值的最小值
                df_pure = df_pure_max - df_pure_min
                nan_iron_order = set(self.time_table.index) - set(df_pure.index)  # 部分铁次号没有数据导致结果中部分铁次缺失，这里把缺失的补上
                df_pure = df_pure.append(pd.Series(np.nan, nan_iron_order)).sort_index().rename(index=(param + '极差'))
                df_pure[df_pure == 0] = np.nan  # 将极差为0的数据置为空值

            res = pd.merge(res, df_pure, how="outer", left_index=True, right_index=True)
        return res

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
            # df['采集项值'] = df['采集项值'].apply(pd.to_numeric)
            df['采集项值'] = pd.to_numeric(df['采集项值'])
            df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
            df = df[['采集项值', '业务处理时间']]
            df = df.set_index('业务处理时间').sort_index()
            df.where(df['采集项值'] < 1e7, inplace=True)  # 去除 999999 的异常值

            res[param] = self.time_table.apply(lambda x: df.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                               axis=1)
            return res
        else:
            df['采集项值'] = pd.to_numeric(df['采集项值'])
            df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])

            df.where(df['采集项值'] < 1e7, inplace=True)

            for item in param:
                df_grouped = df.groupby("采集项名称").get_group(item)
                df_grouped = df_grouped[['采集项值', '业务处理时间']]

                df_grouped = df_grouped.set_index('业务处理时间').sort_index()
                df_rsp = df_grouped.resample('1T').mean()  # 缩小数据大小 1分钟 一次的

                res[item] = self.time_table.apply(lambda x: df_rsp.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                                  axis=1)
            return res

    def get_df(self, param):
        return get_df(param, self.table)  # df

    def get_noumenon0(self):
        """
        '炉顶温度1',  '炉顶温度2', '炉顶温度3', '炉顶温度4',
        '炉顶煤气CO', '炉顶煤气CO2', '炉顶煤气H2'
        '炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6', '炉喉温度7', '炉喉温度8'
        '炉喉温度极差', '炉顶温度极差'
        '炉顶温度', '炉喉温度'
        :return:
        """
        param_list = ['炉顶温度1', '炉顶温度2', '炉顶温度3', '炉顶温度4', '炉顶煤气CO', '炉顶煤气CO2', '炉顶煤气H2',
                      '炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6', '炉喉温度7', '炉喉温度8']
        df = self.get_df(param_list[0])
        res = self.process_business_time(df, param_list)
        res['炉顶温度'] = res[['炉顶温度1', '炉顶温度2', '炉顶温度3', '炉顶温度4']].mean(axis=1)
        res['炉喉温度'] = res[['炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6',
                           '炉喉温度7', '炉喉温度8']].mean(axis=1)
        res['煤气利用率'] = res['炉顶煤气CO2'] * 100 / (res['炉顶煤气CO2'] + res['炉顶煤气CO'])

        # 以下为极差指标处理
        # res_temp = pd.DataFrame()
        range_param_list = ['炉顶温度1', '炉顶温度2', '炉顶温度3', '炉顶温度4',
                            '炉喉温度1', '炉喉温度2', '炉喉温度3', '炉喉温度4', '炉喉温度5', '炉喉温度6', '炉喉温度7', '炉喉温度8']
        res_temp = self.process_business_time(df, range_param_list, range_=True)
        res['炉顶温度极差'] = res_temp[['炉顶温度1极差', '炉顶温度2极差', '炉顶温度3极差', '炉顶温度4极差']].mean(axis=1)
        res['炉喉温度极差'] = res_temp[['炉喉温度1极差', '炉喉温度2极差', '炉喉温度3极差', '炉喉温度4极差', '炉喉温度5极差',
                                  '炉喉温度6极差', '炉喉温度7极差', '炉喉温度8极差']].mean(axis=1)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_noumenon1(self):
        """
        ['炉腰温度1', '炉腰温度2', '炉腰温度3', '炉腰温度4', '炉腰温度5', '炉腰温度6',
         '炉身下一层温度1', '炉身下一层温度2', '炉身下一层温度3', '炉身下一层温度4',
         '炉身下一层温度5', '炉身下一层温度6', '炉身下一层温度7', '炉身下一层温度8',
         '炉身下二层温度1', '炉身下二层温度2', '炉身下二层温度3', '炉身下二层温度4',
         '炉身下二层温度5', '炉身下二层温度6', '炉身下二层温度7', '炉身下二层温度8', '鼓风动能', '理论燃烧温度']
        """
        param_list = ['炉腰温度1', '炉腰温度2', '炉腰温度3', '炉腰温度4', '炉腰温度5', '炉腰温度6',
                      '炉身下一层温度1', '炉身下一层温度2', '炉身下一层温度3', '炉身下一层温度4',
                      '炉身下一层温度5', '炉身下一层温度6', '炉身下一层温度7', '炉身下一层温度8',
                      '炉身下二层温度1', '炉身下二层温度2', '炉身下二层温度3', '炉身下二层温度4',
                      '炉身下二层温度5', '炉身下二层温度6', '炉身下二层温度7', '炉身下二层温度8', '鼓风动能', '理论燃烧温度']

        furnace_shells2 = ['炉身下二层温度1', '炉身下二层温度2', '炉身下二层温度3', '炉身下二层温度4',
                           '炉身下二层温度5', '炉身下二层温度6', '炉身下二层温度7', '炉身下二层温度8']

        df = self.get_df(param_list[0])
        res = self.process_business_time(df, param_list)
        res['炉腰温度'] = res[['炉腰温度1', '炉腰温度2', '炉腰温度3', '炉腰温度4', '炉腰温度5', '炉腰温度6']].mean(axis=1)
        res['炉身下二段温度'] = res[furnace_shells2].mean(axis=1)

        # 计算炉身下二段温度极差
        furnace_shells2_range = self.process_business_time(df, furnace_shells2, range_=True)
        res['炉身下二段温度极差'] = furnace_shells2_range.mean(axis=1)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_noumenon2(self):
        """
        '炉缸温度1', '炉缸温度2', '炉缸温度3', '炉缸温度4', '炉缸温度5', '炉缸温度6',
        '炉底温度1', '炉底温度2', '炉底温度3', '炉底温度4', '炉底温度5', '炉底温度6',
        """
        param_list = ['炉缸温度1', '炉缸温度2', '炉缸温度3', '炉缸温度4', '炉缸温度5', '炉缸温度6',
                      '炉底温度1', '炉底温度2', '炉底温度3', '炉底温度4', '炉底温度5', '炉底温度6',
                      '炉缸中心温度', ]
        df = self.get_df(param_list[0])
        res = self.process_business_time(df, param_list)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_iron_temp(self):
        """
        '铁水温度'
        :return:
        """
        res = pd.DataFrame()
        param_list = ['铁水温度(东)', '铁水温度(西)']
        df = self.get_df(param_list[0])
        res_temp = self.process_business_time(df, param_list, agg_func=np.mean)
        res['铁水温度'] = res_temp.mean(axis=1)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_coke_load(self):
        """
        '焦炭负荷'
        :return:
        """
        # res = pd.DataFrame()
        param_list = ['焦炭负荷']
        df = self.get_df(param_list[0])
        res = self.process_business_time(df, param_list, agg_func=np.mean, resample_=True)
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_molten_iron(self):
        """
        '[C]', '[Ti]', '[Si]', '[S]'
        delta[Ti]  后一个减去前一个。
        :return:
        """
        param_list = ['[C]', '[Ti]', '[Si]', '[S]']
        df = self.get_df(param_list[0])
        res = process_iron(df, param_list, np.mean)
        res['[Ti]+[Si]'] = res['[Ti]'] + res['[Si]']
        res['delta[Ti]'] = res['[Ti]'].diff()

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_slag(self):
        """
        (TiO2) (SiO2) (CaO) (MgO) (Al2O3)
        R2 = CaO/SiO2  R3 = (CaO+MgO)/SiO2  R4 = (CaO+MgO)/(SiO2+Al2O3) 镁铝比 = MgO / Al2O3
        δR2 同 delta[Ti]
        :return:
        """
        param_list = ['(TiO2)', '(SiO2)', '(CaO)', '(MgO)', '(Al2O3)']
        df = self.get_df(param_list[0])
        res = process_iron(df, param_list, np.mean)

        res['R2'] = res['(CaO)'] / res['(SiO2)']
        res['R3'] = (res['(CaO)'] + res['(MgO)']) / res['(SiO2)']
        res['R4'] = (res['(CaO)'] + res['(MgO)']) / (res['(SiO2)'] + res['(Al2O3)'])
        res['镁铝比'] = res['(MgO)'] / res['(Al2O3)']  # 有一条明显比较怪的数据, 需要后期核查
        res['deltaR2'] = res['R2'].diff()
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_ratio(self):
        """
        铁次铁量,喷吹速率,焦比,煤比,燃料比,出铁次数/出铁时间  粉焦比

        日喷煤量： 用喷吹速率推算 铁次煤量
        :return:
        """
        # 计算铁量
        df = self.get_df('受铁重量')

        res = process_iron(df, ['受铁重量'], np.sum)
        res.rename(columns={'受铁重量': '铁次铁量'}, inplace=True)  # 发现有一些铁次铁量是 0, 需要后期核查

        # 计算焦量, 焦比
        param_list = ['冶金焦（自产）', '小块焦']
        param = param_list[0]
        df_coke = self.get_df(param)
        df_coke = self.time2order(df_coke)
        df_coke = process_iron(df_coke, param_list, np.sum)
        res['焦比'] = (df_coke['冶金焦（自产）'] + df_coke['小块焦']) / res['铁次铁量'] * 1000

        # 计算喷煤 煤比
        df_mei = self.process_big_time('喷吹速率')
        d = self.time_table['受铁结束时间'] - self.time_table['受铁开始时间']
        df_mei['d'] = d / pd.to_timedelta('1min')

        res['喷吹速率'] = df_mei['喷吹速率']
        res['出铁次数/出铁时间,min'] = 1 / df_mei['d']
        res['日喷煤量'] = df_mei['d'] * df_mei['喷吹速率']
        res['煤比'] = df_mei['d'] * df_mei['喷吹速率'] / res['铁次铁量'] * 20
        # 燃料比
        res['燃料比'] = res['煤比'] + res['焦比']

        res['粉焦比'] = res['煤比'] / res['焦比']
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_wind(self):
        """
        送风风量,热风压力,炉顶压力,标准风速,热风温度
        实际风速 = 标准风速*(0.101325/273)*((273+风温)/(风压/10+0.101325))
        透气性指数 = 送风风量 / (热风压力 - 炉顶压力1,2) * 100
        压差
        :return:
        """
        res = self.process_big_time(['送风风量', '热风压力', '标准风速', '热风温度', '富氧量', '风口总面积', '富氧压力'], self.get_df('送风风量'))
        res2 = self.process_big_time(['炉顶压力1', '炉顶压力2'], self.get_df('炉顶压力1'))
        res['炉顶压力'] = res2.mean(axis=1)
        res['实际风速'] = res['标准风速'] * (0.101325 / 273) * ((273 + res['热风温度']) / (res['热风压力'] / 1000 + 0.101325))
        res['透气性指数'] = res['送风风量'] / (res['热风压力'] - res['炉顶压力']) * 100
        res['压差'] = res['热风压力'] - res['炉顶压力']
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

    def __process_chemical(self, list2, df):
        """
        专门处理只有上料批次号的指标

        注意：
            1. 数据特点, 没有 业务处理时间 有上料批次号 处理料的化验
            2. 焦炭热性能_CSR 这玩意 一天一采集, 必须以数据为模板
            3. 应该确保上料批次号符合这样的格式: 191013xxxxxxx-2401
        :param list2      处理的指标集合list类型，序号为0，2这样的偶数的，为输出的指标名，奇数为SQL数据库中的指标名
                          例如 ['M40', '焦炭粒度、冷强度_M40'] 输出的名字是'M40', 在数据表里是 '焦炭粒度、冷强度_M40'
        :param df         需要外部处理好DataFrame对象，再传递给本函数
        """

        def to_time(x):
            """
            可能会花费一些时间
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
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        res = pd.DataFrame()
        for i, item in enumerate(param_path):
            param = list3[i]
            group_name = list1[i]
            if item is not None:

                # 需要对 检化验数据 写单独的处理函数

                # 源数据无指标的处理—————赋值为nan继续运行。
                try:
                    df_grouped = df.groupby("采集项名称").get_group(group_name)
                except KeyError:
                    print("数据批次代码", self.table, "无指标" + group_name + "的任何数据")
                    res[group_name] = None
                else:

                    # 应该确保上料批次号符合这样的格式: 191013xxxxxxx-2401
                    df_grouped.loc[:, '业务处理时间'] = df_grouped['上料批号'].apply(to_time)

                    if self.five_lag:  # 如果需要滞后
                        df_grouped.loc[:, '业务处理时间'] = df_grouped['业务处理时间'] - pd.to_timedelta('5h')

                    df_grouped.set_index('业务处理时间', inplace=True)
                    df_rsp = df_grouped.resample('1T').mean().ffill()
                    res[param] = self.time_table.apply(lambda x: df_rsp.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                                       axis=1)
                    res[param] = res[param].ffill()
            else:
                res[group_name] = None  # 专门对烧结5mm的处理， 第一批数据没用 第二批数据有

        return res

    def get_chemical(self):
        """
        数据特点：没有业务处理时间但是有上料批次号
        焦炭热性能_CSR这样一天一采集的指标必须以数据为模板。
        上料质量表。

        上料批次号有两种命名模式 分别调用了两个私有方法
        """
        # 同get_slag_amount方法的处理把所有的化验指标处理
        param_table = pd.read_excel(ORGANIZE_CONFIG_XLSX)
        param_list_chemical = list(param_table[CHEMICAL_TABLE_NAME].dropna())

        # 摘出去那些采集编号代字母的 __process_chemical处理不了的
        group_can = []
        group_cannt = []  # 高炉沟下烧结矿粒度 类的指标分到这里
        for i in param_list_chemical:
            if len(i) >= 9 and i[:9] == '高炉沟下烧结矿粒度':
                group_cannt.append(i)
            else:
                group_can.append(i)

        self.__process_shaojie(group_cannt)  # 调用__process_shaojie 处理高炉沟下烧结去

        param_list_loading = adaptive(group_can)  # 适配
        df = self.get_df(param_list_chemical[0])
        res = self.__process_chemical(param_list_loading, df)

        self.res = pd.merge(res, self.res, how="outer", left_index=True, right_index=True)
        return res

    def __process_shaojie(self, param_list):
        """
        处理烧结<5mm数据
            输出名               SQL库字段名
        '烧结矿<5mm比例,%'  '高炉沟下烧结矿粒度_筛分指数(<5mm)'

        注意：
            第一批数据没有这个烧结，其采集频率为一天左右。
        :return:
        """

        res = pd.DataFrame()
        # param = param_list
        # out_name = param_list
        for param in param_list:
            out_name = param  # 输出指标名
            # try-except 应对有时候数据里面没有烧结矿.
            try:
                df = self.get_df(param)
            except TypeError:
                print("可能SQL数据中没有 %s " % param)
                res[out_name] = np.nan
            else:
                df = df.groupby('采集项名称').get_group(param)
                # 格式化
                df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
                df['采集项值'] = pd.to_numeric(df['采集项值'])

                df_mean = df.groupby('业务处理时间').mean()

                df_continue = df_mean.resample('1T').mean().ffill()  # 连续化
                self.res[out_name] = self.time_table.apply(
                    lambda x: df_continue.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(), axis=1)

        # self.res = pd.merge(res, self.res, how="outer", left_index=True, right_index=True)
        return None

    def get_slag_amount(self):
        """
        铁次渣量:
        [40赤块_CaO*40赤块+冶金焦综合样_CaO*冶金焦（自产）+南非块矿_CaO*南非块矿+小块焦_CaO*小块焦+
        烧结矿成分_CaO*烧结矿+白马球团_CaO*白马球团+酸性烧结矿_CaO*酸性烧结矿]/(CaO)

        渣铁比,kg/t = 铁次渣量 / 铁次铁量

        ※ 对本函数进行测试，运行时需要注意：
           需要先调用 get_ratio get_slag
            sol.get_ratio()
            sol.get_slag()
            sol.get_slag_amount()
        :return:
        """
        # res = pd.DataFrame()
        # list1 = "40赤块_CaO         40赤块_CaO " \
        #         "冶金焦综合样_CaO   冶金焦综合样_CaO " \
        #         "南非块矿_CaO       南非块矿_CaO " \
        #         "小块焦_CaO         小块焦_CaO " \
        #         "烧结矿成分_CaO     烧结矿成分_CaO " \
        #         "白马球团_CaO       白马球团_CaO " \
        #         "酸性烧结矿_CaO     酸性烧结矿_CaO".split()

        # 要处理的上料成分表指标 统一读入 organize/config/20数据表各个名称罗列.xlsx
        param_table = pd.read_excel(ORGANIZE_CONFIG_XLSX)
        param_list_loading = list(param_table[SLAG_TABLE_NAME])  # 西昌2#高炉-上料成分表中所有采集项名称搞出来
        param_list_loading = adaptive(param_list_loading)  # 适配一下
        df = self.get_df(param_list_loading[0])
        res = self.__process_chemical(param_list_loading, df)  # process_chemical函数能保证数据源中无指标时输出为nan
        self.res[res.columns] = res  # 输出结果

        param_list = "40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()
        param = param_list[0]
        df_coke = self.get_df(param)
        df_coke = self.time2order(df_coke)
        df_coke = process_iron(df_coke, param_list, np.sum)

        # res['焦比'] = (df_coke['冶金焦（自产）'] + df_coke['小块焦'])
        res.fillna(0, inplace=True)
        df_coke.fillna(0, inplace=True)  # 矿石没有数据就当是0了

        # 输出整理好的 球团矿比例 和各个矿石的量
        res[df_coke.columns] = df_coke
        res['球团矿比例'] = df_coke['白马球团'] / df_coke.sum(axis=1)

        res['铁次渣量'] = 0
        for i in range(7):
            res['铁次渣量'] = res['铁次渣量'] + res.iloc[:, i] * df_coke.iloc[:, i]
        res['铁次渣量'] = res['铁次渣量'] / self.res['(CaO)']  # 问题: 铁次区间没有 加矿呢???
        res['铁次渣量 / 铁次铁量'] = res['铁次渣量'] / self.res['铁次铁量']

        out_list = ['铁次渣量', '铁次渣量 / 铁次铁量'] + ['球团矿比例'] + list(df_coke.columns)  # 输出指标名
        self.res = pd.merge(res.loc[:, out_list], self.res, how="outer", left_index=True,
                            right_index=True)
        return res

    def get_rule(self):
        """
        # 计算的不对

        # 计算探尺差
        # 各个探尺的悬料
        # 西昌2#高炉采集数据表_上料系统
        """
        df = self.get_df('探尺（南）')
        # 格式化
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        if self.five_lag:  # 如果需要滞后
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

            # 计算有没有悬料：
            xuan = hooker.sort_index()

            xuan['diff'] = xuan.diff()
            temp = xuan.where(xuan['diff'] == 0).dropna()
            xuan_res = temp.where(temp[hooker_name] > 1.5).dropna()

            xuan_time_table = self.time_table
            xuan_time_table['next_start'] = xuan_time_table['受铁开始时间'].shift(-1)

            self.res[hooker_name + '悬料'] = xuan_time_table.apply(
                lambda x: xuan_res.loc[x['受铁开始时间']:x['next_start'], :].shape[0], axis=1)

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

    def get_use_ratio(self):
        """
        获取高炉每小时利用系数
        :return:
        """
        self.res['每小时高炉利用系数'], _ = get_iron_speed(self.table)
        return self.res['每小时高炉利用系数']


def main(table_id, five_lag=True):
    """
    本module 调用入口
    :param table_id: 数据的ID号
    :param five_lag: 是否进行5小时滞后处理
    :return:
    """
    obj = Solution(table=table_id, five_lag=five_lag)
    obj.get_molten_iron()
    obj.get_noumenon0()  # 高炉本体0
    obj.get_noumenon1()  # 高炉本体1
    obj.get_noumenon2()  # 高炉本体2
    obj.get_iron_temp()  # 铁水温度
    obj.get_coke_load()
    obj.get_slag()
    obj.get_wind()
    obj.get_gas()
    obj.get_ratio()
    obj.get_chemical()
    obj.get_rule()
    obj.get_slag_amount()
    obj.get_use_ratio()

    ans = obj.res
    # ans[ans == np.inf] = np.nan  # 因为有些铁次铁量为0 从而导致一些煤比 焦比等铁量衍生指标 算出 inf, np.nan填充

    # 输出excel文件
    if not five_lag:
        ans.to_excel("organize/cache/铁次无滞后_{}.xlsx".format(table_id))  # 因为铁次产量为0 搞出不少 inf
    else:
        ans.to_excel("organize/cache/铁次5h滞后_{}.xlsx".format(table_id))  # 因为铁次产量为0 搞出不少 inf

    return None
