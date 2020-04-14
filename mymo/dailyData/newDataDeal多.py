import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import tool 

# 整理一般性的指标：即只需要重采样的指标
parasName = '炉身下二层温度'
savePath = 'D:/数据/' + parasName + '.xlsx'
dataPath1 = 'D:/数据/西昌2#高炉采集数据表_高炉本体(炉缸1).xlsx'

df1 = tool.readSheet(dataPath1) # 读取数据
split_sort1 = tool.dealDataWithDealtime(df1)
newData = tool.decreaseSampleFreq(split_sort1[parasName], '1D')

# # 煤气利用率
# newData1 = tool.decreaseSampleFreq(split_sort1['炉顶煤气CO'], '1D')
# newData2 = tool.decreaseSampleFreq(split_sort1['炉顶煤气CO2'], '1D')
# newData = (newData2) / (newData1+newData2) * 100

# newData.fillna(newData.mean(), inplace=True) # 均值填充
with pd.ExcelWriter(savePath) as writer:
    newData.to_excel(writer)


# 需要计算的指标：处理方式是先生成公式内的指标，读入指标，计算，然后输出
dataPath1 = 'D:/数据/热风压力.xlsx'
dataPath2 = 'D:/数据/送风风量.xlsx'
dataPath3 = 'D:/数据/炉顶压力.xlsx'

savePath = 'D:/数据/透气性指数.xlsx'
df1 = tool.readSheet(dataPath1) # 读取数据 
df2 = tool.readSheet(dataPath2) # 读取数据 
df3 = tool.readSheet(dataPath3) # 读取数据 


# split_sort1 = tool.dealDataWithDealtime(df1)
# split_sort2 = tool.dealDataWithDealtime(df2)
# split_sort3 = tool.dealDataWithDealtime(df3)

# newData = tool.decreaseSampleFreq(split_sort['炉顶压力1'], '1D')
newData = df2['采集项值'] / (df1['采集项值'] - df3['采集项值']) * 100

with pd.ExcelWriter(savePath) as writer:
    newData.to_excel(writer)


### 温度 ###
dataPath1 = 'D:/Proj-PerformanceGrade/data/西昌2#高炉数据19年10-11月/origin/西昌2#高炉采集数据表_高炉本体(炉缸1).xlsx'
savePath = 'E:/project_data/report/2new炉身下二层温度.xlsx'

df = tool.readSheet(dataPath1) # 读取数据 
split_sort1 = tool.dealDataWithDealtime(df)

luShenXiaErCheng = []
newData1 = []
newData = []

# 搜索key中所有炉身下二层
for value in split_sort1.keys():
    if(value[:4] == '炉身下二'):
        luShenXiaErCheng.append(value)

# 所有炉身下二层
for value in luShenXiaErCheng:
    newData1.append(tool.decreaseSampleFreq(split_sort1[value], '1D'))

# for j in range(len(newData1)):
#     newData1[j].fillna(newData1[j].mean(), inplace=True)

for i in range(len(newData1[0])):
    sum = 0
    for j in range(len(newData1)):
        sum = sum + newData1[j][i]
    newData.append(sum/len(newData1))
    
newData = pd.DataFrame(data=newData, index=newData1[0].index, columns=['采集项值'])
with pd.ExcelWriter(savePath) as writer:
    newData.to_excel(writer)

### 温度 ###
dataPath1 = 'D:/Proj-PerformanceGrade/data/西昌2#高炉数据19年10-11月/origin/西昌2#高炉采集数据表_高炉本体(炉缸1).xlsx'
savePath = './2new炉身下二层温度.xlsx'

df = tool.readSheet(dataPath1) # 读取数据 
split_sort1 = tool.dealDataWithDealtime(df)

luShenXiaErCheng = []
newData1 = {}

# 搜索key中所有炉身下二层
for value in split_sort1.keys():
    if(value[:4] == '炉身下二'):
        luShenXiaErCheng.append(value)

# 所有炉身下二层存进字典
for value in luShenXiaErCheng:
    newData1[value] = tool.decreaseSampleFreq(split_sort1[value], '1D')

# 求取所有温度的平均值
newData = pd.DataFrame(newData1).mean(axis=1).rename(index='炉身下二层温度')
with pd.ExcelWriter(savePath) as writer:
    newData.to_excel(writer)



### 温度极差 ###
# # 以下代码是计算6小时数据用的
# def get0(i, j, index):
#     index.append(pd.to_datetime(split_sort1[luShenXiaErCheng[i]].index[j][:11] + '6:00:00'))
# def get1(i, j, index):
#     index.append(pd.to_datetime(split_sort1[luShenXiaErCheng[i]].index[j][:11] + '12:00:00'))
# def get2(i, j, index):
#     index.append(pd.to_datetime(split_sort1[luShenXiaErCheng[i]].index[j][:11] + '18:00:00'))
# def get3(i, j, index):
#     index.append(pd.to_datetime(split_sort1[luShenXiaErCheng[i]].index[j][:11] + '00:00:00'))
# funcDict = {0: get0, 1: get1, 2: get2, 3: get3}


dataPath1 = 'E:/数据分析/西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).xlsx'
savePath = 'E:/project_data/report/2new炉喉温度极差.xlsx'

df = tool.readSheet(dataPath1) # 读取数据 
split_sort1 = tool.dealDataWithDealtime(df)

newData = []
newData1Df = None

luShenXiaErCheng = [] 
for value in split_sort1.keys():
    if(value[:4] == '炉身下二'):
        luShenXiaErCheng.append(value)

# 修改index，去掉时分秒
index = [] # 存储新的index
for i in range(len(luShenXiaErCheng)):
    index = [] # 存储新的index
    for j in range(len(split_sort1[luShenXiaErCheng[i]])):
        index.append(split_sort1[luShenXiaErCheng[i]].index[j][: 10])
        # funcDict[int(split_sort1[luShenXiaErCheng[i]].index[j][11: 13]) // 6](i, j, index)  
    split_sort1[luShenXiaErCheng[i]].index = index

# 计算每一个温度1，2，3等的极差
newPartData = {} 

for value in luShenXiaErCheng:
    newData1Df = pd.DataFrame({'业务处理时间': split_sort1[value].index, 
                                '采集项值': split_sort1[value].values})
    max = newData1Df.groupby('业务处理时间').apply(np.max)
    min = newData1Df.groupby('业务处理时间').apply(np.min)
    newPartData[value] = max['采集项值'] - min['采集项值']

# 计算总的平均
newData = pd.DataFrame(newPartData).mean(axis='columns', skipna=False)
with pd.ExcelWriter(savePath) as writer:
    newData.to_excel(writer)