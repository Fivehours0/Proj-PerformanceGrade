# -*- coding: utf-8 -*-
import pandas as pd

def load_excel(path, sheets = 2): 
    '''
    函数功能描述:
        处理多sheet的excel表的读取,
        适用于第一个sheet有表头,其他sheet没有表头的情况
    参数说明:
        path: Type str; excel路径
        sheets: Type int; sheet个数,当数值大于等于2时安装多sheet处理
    '''
    if sheets == 1:
        file = pd.read_excel(path)
    else:
        file = pd.read_excel(path, sheet_name = None, header = None)
        file = pd.concat(file)
        file.columns = list(file.iloc[0])
        file = file.drop(index=file.index[0])      
    return file

path = './data/西昌2#高炉数据19年12月-20年2月/origin/'

## 单打独斗
file = '西昌2#高炉采集数据表_上料系统.xlsx'
df = load_excel(path+file)
df.to_pickle('./data/西昌2#高炉数据19年12月-20年2月/pkl/'+file[:-5]+'.pkl')

## 一锅端
# file_list = ['西昌2#高炉-炉渣成分表.xlsx',
#              '西昌2#高炉-上料质量表.xlsx',
#              '西昌2#高炉-铁水实绩表.xlsx',
#              '西昌2#高炉-上料实绩表.xlsx',
#              '西昌2#高炉-铁水成分表.xlsx',
#              '西昌2#高炉采集数据表_送风系统.xlsx',
#              '西昌2#高炉采集数据表_上料系统.xlsx',
#              '西昌2#高炉采集数据表_喷吹系统.xlsx']
# for file in file_list:
#     df = load_excel(path+file)
#     df.to_pickle('./data/西昌2#高炉数据19年12月-20年2月/pkl/'+file[:-5]+'.pkl')