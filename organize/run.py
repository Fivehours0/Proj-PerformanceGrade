"""
一次性生成
整理好的铁次、天数据
"""
import pandas as pd
from organize.iron import main as imain
from organize.day import main as dmain
from organize.extract_and_fill import main as emain


def main(t_id):
    # t_id = 201  # 数据的ID号

    print("开始整理数据id号为{},且带有滞后5小时的铁次数据".format(t_id))
    imain(table_id=t_id, five_lag=True)

    print("开始整理数据id号为{},且不有滞后5铁次数据".format(t_id))
    imain(table_id=t_id, five_lag=False)

    print("开始整理数据id号为{}每日数据".format(t_id))
    dmain(table_id=t_id)

    print("开始对100指标抽取出21,41版本, 并且进行缺失填充")
    path = "organize/cache/"
    files = ["铁次无滞后.xlsx",
             "铁次5h滞后.xlsx",
             "每日.xlsx"]
    for f in files:
        emain(path, f)

    return None
