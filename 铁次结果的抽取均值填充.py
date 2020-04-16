import pandas as pd

PARAM21 = "每小时高炉利用系数	燃料比	焦炭负荷	送风风量	鼓风动能	炉喉温度极差	煤气利用率	" \
          "探尺差	铁水温度	[Ti]	[S]	R2	(TiO2)	炉身下二段温度	M40	CSR".split()

PARAM46 = "每小时高炉利用系数	燃料比	煤比	焦炭负荷	透气性指数	送风风量	实际风速	鼓风动能	炉腹煤气量指数	" \
          "理论燃烧温度	炉顶温度	炉顶温度极差	炉喉温度极差	煤气利用率	探尺差	铁水温度	[Ti]	[Si]	[S]	R2	R3	" \
          "(TiO2)	镁铝比	炉身下二段温度	M40	CSR	[S]	[C]	delta[Ti]	deltaR2	M10	CRI".split()

PATH_MISS = '铁次无滞后结果_100版本_有缺失.xlsx'
if __name__ == '__main__':
    # 有缺失
    df = pd.read_excel(PATH_MISS, index_col=0)
    # 21 的抽取指标
    df21 = df[PARAM21]
    df21.to_excel('铁次无滞后结果_21版本_有缺失.xlsx', sheet_name='21')
    # 46 的抽取
    df46 = df[PARAM46]
    df46.to_excel('铁次无滞后结果_46版本_有缺失.xlsx', sheet_name='46')

    # 均值填充
    ndf = df.fillna(df.mean())
    ndf.to_excel('铁次无滞后结果_100版本_均值填充.xlsx')
    # 21 的抽取指标
    df21 = ndf[PARAM21]
    df21.to_excel('铁次无滞后结果_21版本_均值填充.xlsx', sheet_name='21')
    # 46 的抽取
    df46 = ndf[PARAM46]
    df46.to_excel('铁次无滞后结果_46版本_均值填充.xlsx', sheet_name='46')
