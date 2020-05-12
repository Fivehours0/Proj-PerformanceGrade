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
from organize2.env import find_table
from organize2.env import get_df
from organize2.env import get_time_table
from organize2.env import get_iron_speed


# CHEMICAL_TABLE_NAME = '西昌2#高炉-上料质量表'  # 处理上料质量表的表名字
# SLAG_TABLE_NAME = '西昌2#高炉-上料成分表'  # 处理上料成分表的表名字

# ORGANIZE_CONFIG_XLSX = 'organize/config/20数据表各个名称罗列.xlsx'  # 处理上料成分表的所有指标的 依照表的文件


class RreIron(LegacyRreIron):  # 充分利用继承的特性

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

        res = pre_res[['[C]', '[Ti]']]
        res['[Ti]+[Si]'] = pre_res['[Ti]'] + pre_res['[Si]']
        res['delta([Ti]+[Si])'] = res['[Ti]+[Si]'].diff() / res['[Ti]+[Si]'].shift(1)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_iron_temp(self):
        """
        处理以下指标：
        铁水温度 delta(铁水温度)
        :return:
        """
        res = pd.DataFrame()
        param_list = ['铁水温度(东)', '铁水温度(西)']
        df = self.get_df(param_list[0])
        res_temp = self.process_business_time(df, param_list, agg_func=np.mean)
        res['铁水温度'] = res_temp.mean(axis=1)
        res['delta(铁水温度)'] = res['铁水温度'].diff() / res['铁水温度'].shift(1)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def get_slag_amount(self):
        """
        处理以下指标：
        40赤块、冶金焦（自产）、南非块矿、小块焦、烧结矿、白马球团、
        酸性烧结矿、块矿比例、球团矿比例、烧结比例、矿石批重


        铁次渣量:
        [40赤块_CaO*40赤块+冶金焦综合样_CaO*冶金焦（自产）+南非块矿_CaO*南非块矿+小块焦_CaO*小块焦+
        烧结矿成分_CaO*烧结矿+白马球团_CaO*白马球团+酸性烧结矿_CaO*酸性烧结矿]/(CaO)

        渣铁比,kg/t = 铁次渣量 / 铁次铁量

        球团矿比例 和各个矿石的量

        ※ 对本函数进行测试，运行时需要注意：
           需要先调用 get_ratio get_slag
            sol.get_ratio()
            sol.get_slag()
            sol.get_slag_amount()
        :return:
        """
        # res = pd.DataFrame()
        list_CaO = "40赤块_CaO 冶金焦综合样_CaO 南非块矿_CaO 小块焦_CaO 烧结矿成分_CaO 白马球团_CaO 酸性烧结矿_CaO".split()
        list_CaO = adaptive(list_CaO)  # 适配一下
        df = self.get_df(list_CaO[0])
        res_CaO = self._process_chemical(list_CaO, df)


        # param_list = "40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()
        # param = param_list[0]
        # df_coke = self.get_df(param)
        # df_coke = self.time2order(df_coke)
        # df_coke = process_iron(df_coke, param_list, np.sum)
        #
        # # res['焦比'] = (df_coke['冶金焦（自产）'] + df_coke['小块焦'])
        # res.fillna(0, inplace=True)
        # df_coke.fillna(0, inplace=True)  # 矿石没有数据就当是0了
        #
        # # 输出整理好的 球团矿比例 和各个矿石的量
        # res[df_coke.columns] = df_coke
        # res['球团矿比例'] = df_coke['白马球团'] / df_coke.sum(axis=1)
        #
        # res['铁次渣量'] = 0
        # for i in range(7):
        #     res['铁次渣量'] = res['铁次渣量'] + res.iloc[:, i] * df_coke.iloc[:, i]
        # res['铁次渣量'] = res['铁次渣量'] / self.res['(CaO)']  # 问题: 铁次区间没有 加矿呢???
        # res['铁次渣量 / 铁次铁量'] = res['铁次渣量'] / self.res['铁次铁量']
        #
        # out_list = ['铁次渣量', '铁次渣量 / 铁次铁量'] + ['球团矿比例'] + list(df_coke.columns)  # 输出指标名
        # self.res = pd.merge(res.loc[:, out_list], self.res, how="outer", left_index=True,
        #                     right_index=True)
        return res_CaO


def interface(table):
    obj = RreIron(table)

    obj.get_molten_iron()
    obj.get_iron_temp()
    obj.get_slag_amount()


    res = obj.res


if __name__ == '__main__':
    import os

    os.chdir('../')
    print(os.getcwd())

    sol = RreIron(201)
    res = sol.get_slag_amount()
    # res = sol.res
