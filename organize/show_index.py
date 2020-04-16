"""
展示数据包中有些那些指标
省的来一次新数据
"""

import pandas as pd
import numpy as np


def main():

    file_list1 = [
        '西昌2#高炉采集数据表_高炉本体(炉缸3).pkl',
        '西昌2#高炉采集数据表_高炉本体(炉缸4).pkl',
        '西昌2#高炉-炉渣成分表.pkl',
        '西昌2#高炉-上料成分表.pkl',
        '西昌2#高炉-铁水质量表.pkl',
        '西昌2#高炉采集数据表_渣铁系统.pkl',
        '西昌2#高炉采集数据表_高炉本体(炉缸1).pkl',
        '西昌2#高炉采集数据表_高炉本体(炉缸2).pkl',
        '西昌2#高炉-上料质量表.pkl',
        '西昌2#高炉-铁水实绩表.pkl',
        '西昌2#高炉-上料实绩表.pkl',
        '西昌2#高炉-铁水成分表.pkl',
        '西昌2#高炉采集数据表_送风系统.pkl',
        '西昌2#高炉采集数据表_上料系统.pkl',
        '西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl',
        '西昌2#高炉采集数据表_喷吹系统.pkl']
    file_list_legacy = [
        '西昌2#高炉采集数据表_高炉本体(炉缸3).pkl',
        '西昌2#高炉采集数据表_高炉本体(炉缸4).pkl',
        '炉渣成分表.pkl',
        '上料成分表.pkl',
        '铁水质量表.pkl',
        '西昌2#高炉采集数据表_渣铁系统.pkl',
        '西昌2#高炉采集数据表_高炉本体(炉缸1).pkl',
        '西昌2#高炉采集数据表_高炉本体(炉缸2).pkl',
        '上料质量表.pkl',
        '铁水实绩表.pkl',
        '上料实绩表.pkl',
        '铁水成分表.pkl',
        '西昌2#高炉采集数据表_送风系统.pkl',
        '西昌2#高炉采集数据表_上料系统.pkl',
        '西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl',
        '西昌2#高炉采集数据表_喷吹系统.pkl']

    # 自动生成第三批数据的指标分列状况
    path = "data/西昌2#高炉数据20年2-4月/pkl/"
    out = pd.DataFrame()
    for i in range(len(file_list1)):
        ans = pd.DataFrame()
        df = pd.read_pickle(path + file_list1[i])
        temp = set(df['采集项名称'])
        ans[file_list1[i][:-4]] = sorted(temp)
        out = pd.merge(out, ans, how='outer', left_index=True, right_index=True)

    out.to_excel("data/第三批数据表各个名称罗列.xlsx")


if __name__ == '__main__':
    main()
