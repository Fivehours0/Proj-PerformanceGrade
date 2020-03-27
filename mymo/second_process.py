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

if __name__ == '__main__':
    """
    对 每小时高炉利用系数进行二次处理
    """
    df_use_ratio = pd.read_excel(r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\一次性\每小时高炉利用系数.xlsx',
                                 index_col=0)
    df_outs = pd.read_excel(r"C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\铁次结果汇总_5h滞后处理v2.0.xlsx",
                            index_col=0)

    df_new = pd.merge(df_outs, df_use_ratio, how='left', left_index=True, right_index=True)

    use_ratio = df_new['每小时高炉利用系数']
    use_ratio = use_ratio.fillna(use_ratio.mean())
    use_ratio.to_excel(r'C:\Users\Administrator\Documents\GitHub\BF-grading-range\data\一次性\每小时高炉利用系数_二次处理后.xlsx')