# -*- coding: utf-8 -*-
import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei'] # 修复图片不显示中文的问题
plt.rcParams['axes.unicode_minus']=False

file = '西昌#2高炉每日整理数据v2.0.xlsx' # 文件名
path ='C:/Users/Administrator/Documents/GitHub/BF-grading-range/result/' # 绝对路径
df = pd.read_excel(path+file, index_col=0) 

for param in range(len(df)):
    plt.figure()
    plt.scatter(x=df.index,y=df.iloc[:,param])
    plt.ylabel(df.columns[param])
    plt.xlabel('日期')
    plt.title(df.columns[param]+'的波动散点图')
    plt.savefig(path+'18年数据散点图/'+str(param)+'.png')
    plt.close()