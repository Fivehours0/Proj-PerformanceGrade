import pandas as pd

"""
合并所有批次数据
"""
paths = [
    r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\organize\cache\19\铁次5h滞后.xlsx',
    r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\organize\cache\20\铁次5h滞后.xlsx',
    r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\organize\cache\201\铁次5h滞后.xlsx',
    r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\organize\cache\all\铁次5h滞后.xlsx'
]

df19 = pd.read_excel(paths[0], index_col=0)
df20 = pd.read_excel(paths[1], index_col=0)
df201 = pd.read_excel(paths[2], index_col=0)

# 手动检查一下是不是所有的表的指标是不是一样多

dfz = pd.concat([df19, df20, df201])

dfz.to_excel(paths[3])

# # 抽取部分 ###########################################################
# PARAM21_IRON = "每小时高炉利用系数	燃料比	焦炭负荷	送风风量	鼓风动能	炉喉温度极差	煤气利用率	" \
#                "探尺差	铁水温度  [Ti]	[S]	R2	(TiO2)	炉身下二段温度	M40	CSR".split()
#
# PARAM46_IRON = "每小时高炉利用系数	燃料比	煤比	焦炭负荷	透气性指数 送风风量 实际风速	鼓风动能	炉腹煤气量指数	" \
#                "理论燃烧温度	炉顶温度	炉顶温度极差	炉喉温度 炉喉温度极差	煤气利用率 探尺差 铁水温度 [C] [Ti] [Si] [S] delta[Ti] R2 R3	" \
#                "(TiO2)	镁铝比 deltaR2 炉身下二段温度 M40 M10 CRI CSR St Ad Mt 粉焦比 烧结矿<5mm比例,%".split()
# df_46 = dfz[PARAM46_IRON]
# df_46.to_excel(r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\organize\cache\all\铁次5h滞后_46.xlsx')