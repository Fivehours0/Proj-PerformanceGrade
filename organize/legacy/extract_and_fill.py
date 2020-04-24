import pandas as pd

PARAM21_IRON = "每小时高炉利用系数	燃料比	焦炭负荷	送风风量	鼓风动能	炉喉温度极差	煤气利用率	" \
               "探尺差	铁水温度  [Ti]	[S]	R2	(TiO2)	炉身下二段温度	M40	CSR 烧结矿<5mm比例,%".split()

# PARAM46_IRON = "每小时高炉利用系数	燃料比	煤比	焦炭负荷	透气性指数 送风风量 实际风速	鼓风动能	炉腹煤气量指数	" \
#                "理论燃烧温度	炉顶温度	炉顶温度极差	炉喉温度极差	煤气利用率 探尺差 铁水温度 [C] [Ti] [Si] [S] R2 R3	" \
#                "(TiO2)	镁铝比	炉身下二段温度	M40	CSR	St delta[Ti]	deltaR2	M10	CRI".split()
PARAM46_IRON = "每小时高炉利用系数	燃料比	煤比	焦炭负荷	透气性指数 送风风量 实际风速	鼓风动能	炉腹煤气量指数	" \
               "理论燃烧温度	炉顶温度	炉顶温度极差	炉喉温度 炉喉温度极差	煤气利用率 探尺差 铁水温度 [C] [Ti] [Si] [S] delta[Ti] R2 R3	" \
               "(TiO2)	镁铝比 deltaR2 炉身下二段温度 M40 M10 CRI CSR St Ad Mt 粉焦比 烧结矿<5mm比例,%".split()

# 每日数据的指标名字
PARAM21_DAY = "日产量 燃料比 焦炭负荷 送风风量 鼓风动能 炉喉温度极差 煤气利用率	探尺差	" \
              "[铁水温度] [Ti]	[S]	R2	(TiO2)	炉身下二段温度	焦炭粒度、冷强度_M40	焦炭热性能_CSR 焦炭工分_St " \
              " 高炉沟下烧结矿粒度_筛分指数(<5mm)".split()

PARAM46_DAY = "日产量 燃料比 煤比 焦炭负荷 透气性指数	送风风量 实际风速 鼓风动能 " \
              " 炉腹煤气量指数 理论燃烧温度 炉顶温度 炉顶温度极差 炉喉温度 炉喉温度极差 煤气利用率 探尺差 " \
              " [铁水温度]  [C] [Ti] [Si] [S] R2 R3 (TiO2) 镁铝比	炉身下二段温度 焦炭粒度、冷强度_M40 " \
              " 焦炭热性能_CSR 焦炭工分_St	" \
              " 高炉沟下烧结矿粒度_筛分指数(<5mm) delta_Ti delta_R2 焦炭粒度、冷强度_M10 焦炭热性能_CRI".split()


# PATH_MISS = '铁次无滞后结果_100版本_有缺失.xlsx'
def extract_check(df_col, params, data_type):
    """
    抽取前检查
    :param df_col 被抽取表的表头or 字段
    :param params 要展示的 21 or 46 指标
    :return:
    """
    params_safe = []  # 安全的可抽取指标

    for item in params:
        if item not in df_col:
            print("在{}型数据整理中, 整理出的所有指标(100)中无：指标{}, 或者抽取的指标名错误".format(data_type, item))
        else:
            params_safe.append(item)

    return params_safe


def main(path, file, data_type):
    """

    :param path:
    :param file:
    :param data_type: 数据类型 天 还是铁次
    :return:
    """
    params21 = None
    params46 = None
    if data_type == 'day':
        params21 = PARAM21_DAY
        params46 = PARAM46_DAY

    elif data_type == 'iron':
        params21 = PARAM21_IRON
        params46 = PARAM46_IRON
    else:
        print("data_type 参数输入错误")

    # 有缺失
    pf = path + file
    df = pd.read_excel(pf, index_col=0)
    # 21 的抽取指标
    safe = extract_check(df.columns, params21, data_type)  # 检查
    df21 = df[safe]
    df21.to_excel(pf[:-5] + '_21版本_有缺失.xlsx', sheet_name='21')
    # 46 的抽取
    safe = extract_check(df.columns, params46, data_type)  # 检查
    df46 = df[safe]
    df46.to_excel(pf[:-5] + '_46版本_有缺失.xlsx', sheet_name='46')

    # 均值填充
    ndf = df.fillna(df.mean())
    ndf.to_excel(pf[:-5] + '_100版本_均值填充.xlsx')
    # 21 的抽取指标
    safe = extract_check(ndf.columns, params21, data_type)  # 检查
    df21 = ndf[safe]
    df21.to_excel(pf[:-5] + '_21版本_均值填充.xlsx', sheet_name='21')
    # 46 的抽取
    safe = extract_check(ndf.columns, params46, data_type)  # 检查
    df46 = ndf[safe]
    df46.to_excel(pf[:-5] + '_46版本_均值填充.xlsx', sheet_name='46')
    return None

# if __name__ == '__main__':
# main()
