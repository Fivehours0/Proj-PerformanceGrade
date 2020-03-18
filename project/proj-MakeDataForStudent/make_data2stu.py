import pandas as pd

path = r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\铁次结果汇总_无滞后处理v1.0.xlsx'
df = pd.read_excel(path)
# for i in df.columns:print(i,end=' ')
reservation = "铁次号 M40 M10 CRI CSR St Ad Mt 喷吹煤Ad,% 喷吹煤St，% 喷吹煤Vd，% 烧结矿转鼓强度,% [C] [Ti] \
                [Si] [S] (TiO2) (SiO2) (CaO) (MgO) (Al2O3) R2 R3 R4 镁铝比 送风风量 热风压力 标准风速 热风温度 炉顶压力 实际风速 \
                透气性指数 炉腹煤气发生量 炉腹煤气量指数 铁次铁量 焦比 喷吹速率 煤比 燃料比 探尺差 炉顶温度 炉顶温度极差 \
                炉喉温度 炉喉温度极差 煤气利用率 炉腰温度 炉身下二段温度  \
                炉腰温度1 炉身下一层温度1 炉缸温度4 \
                炉缸温度6 炉底温度3  炉顶煤气CO 炉顶煤气CO2 炉顶煤气H2 鼓风动能 理论燃烧温度 炉缸中心温度 铁水温度 富氧量 风口总面积\
                富氧压力 焦炭负荷 ".split()
rsv = df[reservation]
rsv = rsv.set_index('铁次号')
rsv = rsv.loc[20128700:20129000, :]
rsv_norm = (rsv - rsv.min()) / (rsv.max() - rsv.min())
# for i in reservation[1:]:
#     rsv[i] = (rsv[i] - rsv[i].min()) / (rsv[i].max() - rsv[i].min())
rsv_norm.to_excel('./data.xlsx', float_format="%.5f")
