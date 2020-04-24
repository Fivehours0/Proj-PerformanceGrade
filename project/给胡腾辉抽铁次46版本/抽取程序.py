import pandas as pd
#  21版本
PARAM21_IRON = "每小时高炉利用系数	燃料比	焦炭负荷	送风风量	鼓风动能	炉喉温度极差	煤气利用率	" \
               "探尺差	铁水温度  [Ti]	[S]	R2	(TiO2)	炉身下二段温度	M40	CSR ".split()

#  46版本
PARAM46_IRON = "每小时高炉利用系数	燃料比	煤比	焦炭负荷	透气性指数 送风风量 实际风速	鼓风动能	炉腹煤气量指数	" \
               "理论燃烧温度	炉顶温度	炉顶温度极差	炉喉温度 炉喉温度极差	煤气利用率 探尺差 铁水温度 [C] [Ti] [Si] [S] delta[Ti] R2 R3	" \
               "(TiO2)	镁铝比 deltaR2 炉身下二段温度 M40 M10 CRI CSR St Ad Mt 粉焦比 ".split()

PATH = '铁次100plus_v3.4.xlsx'
df = pd.read_excel(PATH)

df46 = df[PARAM46_IRON]
df46.to_excel('铁次100plus_v3.4_抽取46.xlsx')

df46 = df[PARAM21_IRON]
df46.to_excel('铁次100plus_v3.4_抽取21.xlsx')