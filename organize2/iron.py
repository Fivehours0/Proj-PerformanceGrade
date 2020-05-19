"""
:describe 按照铁次整理数据
:author 夏尚梓 auxiliary 杜智辉
:version v3.5

钢厂二审新指标

注意：
1. 进来新数据时需要 运行MakePickle.py 转成pkl文件，
2. 运行ShowIndex.py 整理出指标excel对照表。不过，新数据可以直接使用 'data/20数据表各个名称罗列.xlsx'

"""
import numpy as np
import pandas as pd

from organize.iron import Solution as LegacyRreIron, process_iron, adaptive


# CHEMICAL_TABLE_NAME = '西昌2#高炉-上料质量表'  # 处理上料质量表的表名字
# SLAG_TABLE_NAME = '西昌2#高炉-上料成分表'  # 处理上料成分表的表名字

# ORGANIZE_CONFIG_XLSX = 'organize/config/20数据表各个名称罗列.xlsx'  # 处理上料成分表的所有指标的 依照表的文件


class PreIron(LegacyRreIron):  # 充分利用继承的特性

    def get_molten_iron(self):
        """
        处理以下指标：
        [C]、[S]、[Ti]+[Si]、delta([Ti]+[Si]

        注意：
            delta([Ti]+[Si]是后一个减去前一个。
        :return:
        """
        param_list = ['[C]', '[Ti]', '[Si]', '[S]']
        df = self.get_df(param_list[0])
        pre_res = process_iron(df, param_list, np.mean)

        res = pre_res[['[C]', '[S]']]
        res['[Ti]+[Si]'] = pre_res['[Ti]'] + pre_res['[Si]']
        res['delta([Ti]+[Si])'] = res['[Ti]+[Si]'].diff()

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_iron_temp(self):
        """
        处理以下指标：
        铁水温度 delta(铁水温度)
        :return:
        """
        res = pd.DataFrame()
        param_list = ['铁水温度(东)', '铁水温度(西)', '出铁速率']
        df = self.get_df(param_list[0])

        res_temp = self.process_business_time(df, param_list, agg_func=np.mean)
        res['铁水温度'] = res_temp[['铁水温度(东)', '铁水温度(西)']].mean(axis=1)
        res['delta(铁水温度)'] = res['铁水温度'].diff()
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def access_mine_batch(self):
        """
        获取矿石的批数
        :return:
        """
        df = self.get_df('烧结矿')
        df_iron = self.time2order(df)  # 找出业务处理时间对应的铁次时间
        df_iron = df_iron.groupby('采集项名称').get_group('烧结矿')
        df_iron_droped = df_iron.where(df_iron['铁次号'] != 0).dropna()
        df_count = df_iron_droped.groupby('铁次号').count()
        return df_count.iloc[:, 0]

    def get_slag_amount(self):
        """
        处理以下指标：
        40赤块、冶金焦（自产）、南非块矿、小块焦、烧结矿、白马球团、酸性烧结矿、
        矿石批重 (以烧结矿批数为准)
        球团矿比例 = 白马球团 / sum(40赤块、冶金焦（自产）、南非块矿、小块焦、烧结矿、白马球团、酸性烧结矿)
        块矿比例 = (南非块矿 + 40赤块)  / sum(40赤块、冶金焦（自产）、南非块矿、小块焦、烧结矿、白马球团、酸性烧结矿)
        烧结比例 = (烧结矿 + 酸性烧结矿) / sum(40赤块、冶金焦（自产）、南非块矿、小块焦、烧结矿、白马球团、酸性烧结矿)
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
        res = pd.DataFrame()

        # 利用钙平衡法计算渣量：1.获取CaO的信息
        list_CaO = "40赤块_CaO 冶金焦综合样_CaO 南非块矿_CaO 小块焦_CaO 烧结矿成分_CaO 白马球团_CaO 酸性烧结矿_CaO".split()
        list_CaO = adaptive(list_CaO)  # 适配一下
        df = self.get_df(list_CaO[0])
        res_CaO = self._process_chemical(list_CaO, df)

        # 获取各个矿石量的信息
        param_list = "40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()
        param = param_list[0]
        df_coke = self.get_df(param)
        df_coke = self.time2order(df_coke)
        df_coke = process_iron(df_coke, param_list, np.sum)

        # 南非块矿_CaO就当0.127  冶金焦综合样_CaO 没有就当是11
        if np.all(res_CaO['冶金焦综合样_CaO'].isna()):
            print("冶金焦综合样_CaO 自动填充为 11")
            res_CaO['冶金焦综合样_CaO'].fillna(11, inplace=True)
        if np.all(res_CaO['南非块矿_CaO'].isna()):
            print("南非块矿_CaO 自动填充为 0.127")
            res_CaO['南非块矿_CaO'].fillna(0.127, inplace=True)

        res_CaO.fillna(0, inplace=True)  # 剩下的矿石的CaO化验值填充为0
        df_coke.fillna(0, inplace=True)  # 矿石没有数据就当是0了
        #
        # 输出整理好的 球团矿比例 和各个矿石的量
        res[df_coke.columns] = df_coke
        temp_sum = df_coke.sum(axis=1)  # 矿石总量

        res['球团矿比例'] = df_coke['白马球团'] / temp_sum
        res['烧结矿比例'] = (df_coke['烧结矿'] + df_coke['酸性烧结矿']) / temp_sum
        res['块矿比例'] = (df_coke['40赤块'] + df_coke['南非块矿']) / temp_sum

        # 矿石批重

        batch = self.access_mine_batch()  # 铁次批数
        mine_sum = df_coke[['40赤块', '南非块矿', '烧结矿', '白马球团', '酸性烧结矿']].sum(axis=1)  # 铁次矿石重量
        res['矿石批重'] = mine_sum / batch

        #
        res['铁次渣量'] = (res_CaO['40赤块_CaO'] * df_coke['40赤块'] +
                       res_CaO['冶金焦综合样_CaO'] * df_coke['冶金焦（自产）'] +
                       res_CaO['南非块矿_CaO'] * df_coke['南非块矿'] +
                       res_CaO['小块焦_CaO'] * df_coke['小块焦'] +
                       res_CaO['烧结矿成分_CaO'] * df_coke['烧结矿'] +
                       res_CaO['白马球团_CaO'] * df_coke['白马球团'] +
                       res_CaO['酸性烧结矿_CaO'] * df_coke['酸性烧结矿'])
        res['铁次渣量'] = res['铁次渣量'] / self.res['(CaO)']  # 另外运行此语句时需要 get_slag() 做前置
        res['铁次渣量 / 铁次铁量'] = res['铁次渣量'] / self.res['铁次铁量']  # 需要 get_ratio() 前置
        #
        # out_list = ['铁次渣量', '铁次渣量 / 铁次铁量'] + ['球团矿比例'] + list(df_coke.columns)  # 输出指标名

        self.res = pd.merge(res, self.res, how="outer", left_index=True,
                            right_index=True)
        return res

    def get_ratio(self):
        """
        铁次铁量,喷吹速率,焦比,煤比,燃料比, 粉焦比

        日喷煤量： 用喷吹速率推算 铁次煤量

        delta(铁次铁量)

        :return:
        """
        # 计算铁量
        df = self.get_df('受铁重量')
        res = process_iron(df, ['受铁重量'], np.sum)
        res.rename(columns={'受铁重量': '铁次铁量'}, inplace=True)  # 发现有一些铁次铁量是 0, 需要后期核查
        res['delta(铁次铁量)'] = res['铁次铁量'].diff()

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
        # res['出铁次数/出铁时间,min'] = 1 / df_mei['d']
        res['日喷煤量'] = df_mei['d'] * df_mei['喷吹速率']
        res['煤比'] = df_mei['d'] * df_mei['喷吹速率'] / res['铁次铁量'] * 20
        # 燃料比
        res['燃料比'] = res['煤比'] + res['焦比']

        res['粉焦比'] = res['煤比'] / res['焦比']
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_wind(self):
        """
        热风压力,炉顶压力,标准风速,热风温度 送风风量 '风口总面积'
        实际风速 = 标准风速*(0.101325/273)*((273+风温)/(风压/10+0.101325))
        透气性指数 = 送风风量 / (热风压力 - 炉顶压力1,2) * 100
        富氧率 = ((0.21*风量)+(富氧量*0.992)) / (风量+富氧量) -0.21
        压差
        :return:
        """
        res0 = self.process_big_time(['送风风量', '热风压力', '标准风速', '热风温度', '富氧量', '风口总面积'], self.get_df('送风风量'))
        res = res0[['送风风量', '热风压力', '热风温度', '风口总面积']]
        res['富氧率'] = ((0.21 * res0['送风风量']) + (res0['富氧量'] * 0.992)) / (res0['送风风量'] + res0['富氧量']) - 0.21
        res2 = self.process_big_time(['炉顶压力1', '炉顶压力2'], self.get_df('炉顶压力1'))
        res['炉顶压力'] = res2.mean(axis=1)
        res['实际风速'] = res0['标准风速'] * (0.101325 / 273) * ((273 + res['热风温度']) / (res['热风压力'] / 1000 + 0.101325))
        res['透气性指数'] = res['送风风量'] / (res['热风压力'] - res['炉顶压力']) * 100
        res['压差'] = res['热风压力'] - res['炉顶压力']
        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)

        return res

    def get_tempe_aver_and_range(self):
        """
        获取获取如下温度均值和极差:
            鼓风动能 炉腹煤气发生量 理论燃烧温度 炉顶煤气CO 炉顶煤气CO2 炉顶煤气H2 煤气利用率 炉缸中心温度
            炉缸中心温度 炉顶平均温度 炉顶温度极差 炉喉平均温度 炉喉温度极差 炉腰平均温度 炉腰温度极差
            炉身下一层温度	炉身下一层温度极差 炉身下二层温度 炉身下二层温度极差 炉缸平均温度 炉缸温度极差
            炉底平均温度	炉底温度极差
        """

        def cal_temperature(data, temp_param):
            """
            根据铁次化后的单点温度数据, 计算平均温度或平均温度极差
            :param data: 铁次化后的单点温度参数或者单点温度极差数据，类型：DataFrame
            :param temp_param: 需要求的平均温度或温度极差参数列表，类型: list
            :return: 返回平均温度或温度极差参数数据，类型: DataFrame
            """
            res_aver_or_range = pd.DataFrame()
            for one_temp in temp_param:

                # 特殊对待'炉身下一层平均温度'和'炉身下二层平均温度'，因为他们的名字比较特别，不能与其他指标一块处理
                if '炉身' in one_temp:

                    # 取出名称中包含有 one_temp[:5] + '温度' 的参数数据，求平均得到平均温度
                    res_aver_or_range[one_temp] = data[
                        list(filter(lambda x: (one_temp[:5] + '温度') in x, data.keys()))].mean(axis=1)

                # '炉缸温度' in '炉缸中心温度'的值为False，故计算炉缸温度时，不会误用炉缸中心温度的数据
                else:

                    # 取出名称中包含有 one_temp[:2] + '温度' 的参数数据，求平均得到平均温度
                    res_aver_or_range[one_temp] = data[
                        list(filter(lambda x: (one_temp[:2] + '温度') in x, data.keys()))].mean(axis=1)

            return res_aver_or_range

        all_table_mean = pd.DataFrame()  # 将5个高炉本体表的铁次数据合并存储在该变量中
        all_table_range = pd.DataFrame()  # 将5个高炉本体表的铁次极差数据合并存储在该变量中
        res_temp = pd.DataFrame()  #

        # 分别是5个高炉本体表中的一个单点温度, 用于获取df数据
        get_df_list = ['炉喉温度1', '炉腰温度1', '炉底温度1', '炉底温度17', '炉缸温度146']

        # 通过公式计算得出和无需处理的参数列表
        direct_simple_list = ['鼓风动能', '炉腹煤气发生量', '理论燃烧温度', '炉顶煤气CO', '炉顶煤气CO2', '炉顶煤气H2', '煤气利用率', '炉缸中心温度']

        # 对单点温度求平均的目标平均温度参数
        direct_mean_list = ['炉顶平均温度', '炉喉平均温度', '炉腰平均温度', '炉身下一层平均温度', '炉身下二层平均温度', '炉缸平均温度', '炉底平均温度']

        # 对单点温度极差求平均的目标极差温度参数
        direct_range_list = ['炉顶温度极差', '炉喉温度极差', '炉腰温度极差', '炉身下一层温度极差', '炉身下二层温度极差', '炉缸温度极差', '炉底温度极差']

        for value in get_df_list:
            df = self.get_df(value)
            param_list = list(set(df['采集项名称']))  # 获取表中所有参数名称

            mean_temp = self.process_business_time(df, param_list)
            all_table_mean = pd.merge(all_table_mean, mean_temp, how="outer", left_index=True, right_index=True)
            range_temp = self.process_business_time(df, param_list, range_=True)
            all_table_range = pd.merge(all_table_range, range_temp, how="outer", left_index=True, right_index=True)

        res_mean = cal_temperature(all_table_mean, direct_mean_list)  # 计算平均温度
        res_range = cal_temperature(all_table_range, direct_range_list)  # 计算温度极差
        res_temp = pd.merge(res_temp, res_mean, how="outer", left_index=True, right_index=True)
        res_temp = pd.merge(res_temp, res_range, how="outer", left_index=True, right_index=True)

        for value in direct_simple_list:
            if value == '煤气利用率':
                res_temp[value] = all_table_mean['炉顶煤气CO2'] * 100 / (
                        all_table_mean['炉顶煤气CO2'] + all_table_mean['炉顶煤气CO'])
            else:
                res_temp[value] = all_table_mean[value]

        self.res = pd.merge(self.res, res_temp, how="outer", left_index=True, right_index=True)
        return res_temp

    def get_use_ratio(self):
        """
        获取高炉每小时利用系数
        出铁速率
        delta出铁速率
        :return:
        """
        df_iron_speed = self.get_df("出铁速率")
        df_iron_speed = df_iron_speed.groupby("采集项名称").get_group("出铁速率")
        # 格式化
        df_iron_speed.loc[:, '采集项值'] = pd.to_numeric(df_iron_speed['采集项值'])
        df_iron_speed.loc[:, "业务处理时间"] = pd.to_datetime(df_iron_speed["业务处理时间"])
        df_iron_speed.loc[:, "业务处理时间"].where(df_iron_speed['采集项值'] < 1e7, inplace=True)
        df_iron_speed.dropna(inplace=True)
        df_time_indexed = df_iron_speed.set_index("业务处理时间").sort_index()

        time_table = self.time_table
        res_temp = time_table.apply(lambda x: df_time_indexed.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
                                    axis=1)
        self.res['出铁速率'] = res_temp
        self.res['delta(出铁速率)'] = res_temp.diff()
        self.res['每小时高炉利用系数'] = res_temp * 60 / 1750
        return None


def interface(table):
    obj = PreIron(table)

    obj.get_molten_iron()
    obj.get_iron_temp()
    obj.get_slag()
    obj.get_ratio()
    obj.get_slag_amount()
    obj.get_wind()
    obj.get_coke_load()  # 焦炭负荷
    obj.get_rule()
    obj.get_use_ratio()  # 高炉利用系数
    obj.get_tempe_aver_and_range()

    ans = obj.res
    ans.to_excel("organize2/铁次5h滞后_{}.xlsx".format(table))  # 因为铁次产量为0 搞出不少 inf
    return ans


# 测试代码区
if __name__ == '__main__':
    import os

    os.chdir('../')
    print(os.getcwd())

    sol = PreIron(19)
    # sol.get_ratio()
    # sol.get_slag()
    sol.get_use_ratio()
    res = sol.res
    # res = interface(201)

# TODO 贴标签
# TODO 铁次->天
