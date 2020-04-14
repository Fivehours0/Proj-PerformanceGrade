"""
使用 momy 的入口

"""
from mymo.dailyData.daily_preprocess100 import *
if __name__ == '__main__':
    # generate_all_gyy_table()
    print("done")
    table = 201
    res0 = []
    res0.append(get_coke(table))
    res0.append(get_molten_iron(table))
    res0.append(get_deltaTi(table))
    res0.append(get_slag(table))
    res0.append(get_delta_R2(table))
    res0.append(get_ratio(table))
    dfs = pd.concat(res0, axis=1)
    dfs.to_excel('每日数据2月以后部分指标.xlsx')