# -*- coding: utf-8 -*-
import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei'] # 修复图片不显示中文的问题
plt.rcParams['axes.unicode_minus']=False

# 18年数据散点分析图
file = '西昌#2高炉每日整理数据v2.0.xlsx' # 文件名
path ='C:/Users/Administrator/Documents/GitHub/BF-grading-range/result/' # 绝对路径
df_18 = pd.read_excel(path+file, index_col=0, sheet_name='18年数据') 
df_19 = pd.read_excel(path+file, index_col=0, sheet_name='19年10月-20年2月') 
df_concat = pd.concat([df_18, df_19])

df = df_concat
for param in range(len(df.columns)):
    plt.figure()
    plt.scatter(x=df.index,y=df.iloc[:,param])
    plt.ylabel(df.columns[param])
    plt.xlabel('日期')
    plt.title(df.columns[param]+'的波动散点图')
    plt.savefig(path+'数据散点图/'+str(param)+'.png')
    plt.close()




# # 对日产量得进一步分析
# path = './data/西昌2#高炉数据19年12月-20年2月/pkl/'
# f = '西昌2#高炉-铁水实绩表.pkl'
# df = pd.read_pickle(path+f)

# df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
# df['采集项值'] = pd.to_numeric(df['采集项值'])
# # df = df[['业务处理时间','采集项值']].set_index('业务处理时间')
# # df = df.groupby('业务处理时间').sum()
# # self.res['日产量'] = df['采集项值']       