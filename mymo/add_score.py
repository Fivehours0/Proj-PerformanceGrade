"""
:describe: 
    可为铁次数据或者每日数据增加系统评分和现场评分
"""
import pandas as pd
from mymo.get_things import get_time_table, get_score_table


class AddScore:
    def __init__(self, iron_data, table, daily_or_iron: bool, save_path=None):
        """
        Parameters
        ----------
            iron_data: 铁次数据 类型: DataFrame or Series, index为铁次号
            daily_or_iron: boolean, 选择为每日数据or铁次数据添加分数, 0为铁次, 1为每日
            save_path: 数据保存的地址 类型: str
        """
        self.iron_data = iron_data
        # 铁次化数据转化为每日数据的参考时间
        self.iron_to_daily_key: str = '受铁结束时间'

        self.table = table
        self.savePath = save_path
        self.daily_or_iron = daily_or_iron

        self.score_data = self.get_score()

    def get_score(self):
        """
            获取系统评分和现场评分分数表
        """
        return get_score_table(self.table)

    def get_iron_time(self):
        """
            获取铁次时间表
        """
        return get_time_table(self.table)

    def add_date(self):
        """
            去掉self.iron_to_daily_key(受铁开始时间或者受铁结束时间)的时分秒, 添加到data中, 用以添加评分, 最后会删除

            即将self.iron_to_daily_key作为铁次转化为每日的时间参考.因为评分表是以日期为参照的, 所以需要添加该列作为对照
        """
        iron_time = self.get_iron_time()[self.iron_to_daily_key]
        iron_time = pd.to_datetime(iron_time).dt.floor('d').rename('日期')
        self.iron_data = pd.merge(self.iron_data, iron_time, how='left', left_index=True, right_index=True)
        return self.iron_data

    def score_calibration(self):
        """
            为每一个样本添加系统评分，现场评分数据
        """
        score_dict = {'铁次': [], '系统评分': [], '现场评分': []}
        for value in self.score_data.index:  # 对系统和现场评分表的时间进行循环
            count = sum(self.iron_data['日期'] == value)  # 日期中等于系统和现场评分表时间value的个数
            score_dict['铁次'].extend(self.iron_data.index[self.iron_data['日期'] == value])
            score_dict['系统评分'].extend([self.score_data.loc[value]['系统评分']] * count)
            score_dict['现场评分'].extend([self.score_data.loc[value]['现场评分']] * count)
        score_df = pd.DataFrame(score_dict).set_index('铁次').sort_index()
        self.iron_data = pd.merge(self.iron_data, score_df, how='left', left_index=True, right_index=True)

    # def add_score_label(self):
    #     """
    #     对系统评分和现场评分按照分数范围(scoreRange)进行标定, 例如大于80小于90的分数标定为0
    #     """
    #     system_label_dict = {'系统铁次号': [], '系统label': []}
    #     scene_label_dict = {'现场铁次号': [], '现场label': []}
    #     label = 0
    #     for i in range(len(self.scoreRange) - 1):
    #         # 为了提取该分数区间段内的数据
    #         sys_condition = (self.iron_data['系统评分'] < self.scoreRange[i]) & (
    #                 self.iron_data['系统评分'] >= self.scoreRange[i + 1])
    #         scene_condition = (self.iron_data['现场评分'] < self.scoreRange[i]) & (
    #                 self.iron_data['现场评分'] >= self.scoreRange[i + 1])
    #         system_label_dict['系统铁次号'].extend(self.iron_data.index[sys_condition])
    #         system_label_dict['系统label'].extend(sum((sys_condition)) * [label])
    #
    #         scene_label_dict['现场铁次号'].extend(self.iron_data.index[scene_condition])
    #         scene_label_dict['现场label'].extend(sum(scene_condition) * [label])
    #         label += 1
    #     iron_and_label1 = pd.DataFrame(system_label_dict).set_index('系统铁次号').sort_index()
    #     iron_and_label2 = pd.DataFrame(scene_label_dict).set_index('现场铁次号').sort_index()
    #     iron_and_label = pd.merge(iron_and_label1, iron_and_label2, how='outer', left_index=True, right_index=True)
    #     self.iron_data = pd.merge(self.iron_data, iron_and_label, how='left', left_index=True, right_index=True)

    def save_data(self):
        """
            保存数据
        """
        if self.savePath is not None:
            self.iron_data.to_excel(self.savePath)

    def start(self, ):
        # 为铁次数据添加分数
        if not self.daily_or_iron:
            self.add_date()  # 为data添加一列日期(格式: 年月日)数据, 用以添加评分数据, 最后会删除
            self.score_calibration()  # 为铁次数据添加评分
            self.iron_data.drop('日期', axis=1, inplace=True)  # 丢弃为添加评分创建的日期列
            # # 为每个铁次样本的分数添加标签
            # self.add_score_label()
            self.save_data()

        # 为每日数据添加分数
        else:
            self.iron_data = pd.merge(self.iron_data, self.score_data, how='left', left_index=True, right_index=True)
            self.save_data()
        print("AddScore Complete!")


def main():
    import os

    os.chdir('../')

    score_path = 'data/分数.xlsx'  # 系统评分和现场评分的整合表
    data_path = 'data/铁次252plus_201_v3.5.xlsx'  # 数据

    save_path = 'data/增加分数.xlsx'  # 数据保存的地址
    table = 201  # 添加铁次时间用

    score = pd.read_excel(score_path).set_index('日期')
    iron_data = pd.read_excel(data_path).set_index('铁次号')

    process = AddScore(iron_data, table=table, daily_or_iron=False, save_path=save_path)
    process.start()


if __name__ == "__main__":
    main()
