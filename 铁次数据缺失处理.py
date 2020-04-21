import pandas as pd
# 修补画图时 中文乱码的问题
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
#  增加 受铁开始结束表

# 铁次时间表的存放路径
IRON_TIME = {19: 'data/西昌2#高炉数据19年10-11月/铁次时间.xlsx',
             20: 'data/西昌2#高炉数据19年12月-20年2月/铁次时间.xlsx',
             201: 'data/西昌2#高炉数据20年2-4月/铁次时间.xlsx'
             # 新数据集合的代码 : 存放"铁次时间.xlsx"文件的路径
             }

df = pd.read_excel('铁次100plus_v3.2.xlsx', index_col=0)

# time_table_19 = pd.read_excel(IRON_TIME[19], index_col=0)
# time_table_20 = pd.read_excel(IRON_TIME[20], index_col=0)
# time_table_201 = pd.read_excel(IRON_TIME[201], index_col=0)

# time_table = pd.concat([time_table_19, time_table_20, time_table_201])

# temp = pd.merge(time_table, df, how='right', left_index=True, right_index=True)
# temp.to_excel('铁次100plus_v3.2.xlsx')
temp = df
# 去除 缺失程度超过 2成的 采集项指标
list_lack = list(temp.columns[temp.count() / temp.shape[0] < 0.8])
print("去除 缺失程度超过 2成的 采集项指标: ")
print(list_lack)
droped = temp.drop(columns=list_lack)

# 去除 缺失程度超过 2成的 样本
list_lack = list(droped.index[droped.count(axis=1) / droped.shape[1] < 0.8])
print("去除 缺失程度超过 2成的 样本")
print(list_lack)
droped = droped.drop(index=list_lack)


# 画图看异常 放弃
# for i in range(2, droped.shape[1]):
#     plt.figure()
#     droped.iloc[:, i].plot()
#
#     plt.close()
# plt.show()
droped.ffill().bfill()

droped.to_excel('temp.xlsx')
