# -*- coding: UTF-8 -*-
from organize.iron import Solution
import os
import pandas as pd


def get_data(table):
    solv = Solution(table)
    solv.get_ratio(True)
    solv.get_slag()
    solv.get_slag_amount(True)
    return solv.res


if __name__ == '__main__':
    os.chdir('../')
    print("work path: ", os.getcwd())

    res = pd.concat([get_data(19), get_data(20), get_data(201)])

    df = pd.read_excel('data/铁次100plus_v3.4.xlsx')

    df = df.iloc[:, :3]
    df.merge(res, how='left', )
    merged = pd.merge(df, res, how='inner', left_on='铁次号', right_index=True)

    merged.set_index('铁次号', inplace=True)
    param_list = "球团矿比例 40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()

    extract = merged[param_list]
    extract = extract.ffill().bfill()
    extract.to_excel('organize/铁次plus100v3.4_球团矿等临时追加.xlsx')
