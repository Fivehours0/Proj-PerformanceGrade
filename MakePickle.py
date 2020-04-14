# -*- coding: utf-8 -*-
import pandas as pd


def load_excel(input_path, sheets=2):
    """
    处理多sheet的excel表的读取, 同时第一个sheet有表头,其他sheet没有表头
    :param input_path: excel路径
    :param sheets: sheet个数,当数值大于等于2时安装多sheet处理
    :return:
    """

    if sheets == 1:
        uncooked = pd.read_excel(input_path)
    else:
        uncooked = pd.read_excel(input_path, sheet_name=None, header=None)
        uncooked = pd.concat(uncooked)
        uncooked.columns = list(uncooked.iloc[0])
        uncooked = uncooked.drop(index=uncooked.index[0])

    return uncooked


if __name__ == '__main__':

    uncooked_path = 'data/西昌2#高炉数据20年2-4月/origin/'  # 没有榨菜过的数据的路径
    cooked_path = 'data/西昌2#高炉数据20年2-4月/pkl/'  # 榨好的路径

    file_list = ['西昌2#高炉-炉渣成分表.xlsx',
                 '西昌2#高炉-上料成分表.xlsx',
                 '西昌2#高炉采集数据表_高炉本体(炉缸3).xlsx',
                 '西昌2#高炉-铁水质量表.xlsx',
                 '西昌2#高炉采集数据表_喷吹系统.xlsx',
                 '西昌2#高炉采集数据表_渣铁系统.xlsx',
                 '西昌2#高炉采集数据表_高炉本体(炉缸1).xlsx',
                 '西昌2#高炉采集数据表_高炉本体(炉缸2).xlsx',
                 '西昌2#高炉-上料质量表.xlsx',
                 '西昌2#高炉-铁水实绩表.xlsx',
                 '西昌2#高炉-上料实绩表.xlsx',
                 '西昌2#高炉-铁水成分表.xlsx',
                 '西昌2#高炉采集数据表_送风系统.xlsx',
                 '西昌2#高炉采集数据表_上料系统.xlsx',
                 '西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).xlsx',
                 '西昌2#高炉采集数据表_高炉本体(炉缸4).xlsx']
    for file in file_list:
        df = load_excel(uncooked_path + file)
        df.to_pickle(cooked_path + file[:-5] + '.pkl')
