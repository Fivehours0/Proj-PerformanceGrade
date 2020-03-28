"""
对铁次型数据进行二次处理
1. 删除某些样本
2. 填充缺失值
"""
import pandas as pd
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# if __name__ == '__main__':
"""
对 每小时高炉利用系数进行二次处理
"""
# df_use_ratio = pd.read_excel(
#     r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\钢研院指标的铁次化数据抽取\每小时高炉利用系数.xlsx',
#     index_col=0)
# df_outs = pd.read_excel(r"C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\铁次结果汇总_5h滞后处理v2.0.xlsx",
#                         index_col=0)
#
# df_new = pd.merge(df_outs, df_use_ratio, how='left', left_index=True, right_index=True)
#
# use_ratio = df_new['每小时高炉利用系数']
# use_ratio = use_ratio.fillna(use_ratio.mean())
# use_ratio.to_excel(
#     r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\钢研院指标的铁次化数据抽取\每小时高炉利用系数_二次处理后.xlsx')

"""
对 每小时高炉利用系数(出铁速率版)进行二次处理
"""
from mymo.iron_product_speed import get_all_iron_speed

df_iron_speed = get_all_iron_speed()
df_module = pd.read_excel("data/铁次结果汇总_5h滞后处理v2.0.xlsx", index_col=0)  # 筛除 < 1min 的模板

df_new = pd.merge(df_module, df_iron_speed, how='left', left_index=True, right_index=True)
answer = df_new['每小时高炉利用系数']

answer.where(answer > 0.001, inplace=True)  # answer[answer < 0.001].count() # 38个 0 值
answer.where(answer < 0.3, inplace=True)  # answer[answer > 0.3].count() # 29个 0.342857 值
answer_interpolated = answer.interpolate()  # 221/1371的缺失率 # 线性填充
# plt.scatter(answer_interpolated.index, answer_interpolated.values)
# plt.show()

answer_interpolated.to_excel('data/钢研院指标的铁次化数据抽取/每小时高炉利用系数(出铁速率版).xlsx')
