# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 19:21:18 2020

@author: Administrator

整理2019年10-11月的非实时指标的6小时数据.

需要以下目录文件:
./pkl/西昌2#高炉采集数据表_渣铁系统.pkl
./pkl/铁水实绩表.pkl
./pkl/上料实绩表.pkl
./pkl/铁水成分表.pkl
./pkl/炉渣成分表.pkl
./pkl/上料质量表.pkl
./铁次时间.xlsx

"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


# 修复图片不显示中文的问题
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False


class Solution:
    
    def __init__(self):
        index = pd.date_range('2019-10-01 0:00:00', '2019-11-30 23:00:00',
                              freq='6h')
        self.res = pd.DataFrame(data=None,index=index)
        
    
    def get_yield_alternate(self):
        
        # 计算产量的备选方法
        ## 用出铁速率 计算6小时产量
        
        df = pd.read_pickle('./pkl/西昌2#高炉采集数据表_渣铁系统.pkl')
        
        df = df.groupby('采集项名称').get_group('出铁速率') # 筛选出 出铁速率
        # 格式转换
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间']) 
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        
        df.set_index('业务处理时间', inplace=True) 
        df.sort_index(inplace=True)
        df.drop(df.columns[0:2], axis=1, inplace=True)
        
        df[df.iloc[:,0] > 10] = None # 去除极端异常值 1e9
        
        daliy = df.resample('24h').sum()
        
        # 10-23号 之后数据 不是1分钟一采集 而是 1小时一采集 缺失太多.
        
        return daliy        
        
    
    def get_yield(self):
        
        df = pd.read_pickle('./pkl/铁水实绩表.pkl')
        iron_time = pd.read_excel('铁次时间.xlsx')
        
        df = df[['铁次号','采集项值']]
        # 格式转换
        df['铁次号'] = pd.to_numeric(df['铁次号'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df.sort_values('铁次号', inplace=True) # 排序
        df.reset_index(drop=True, inplace=True)
        df = df.groupby('铁次号').sum() # 合并同铁次不同罐号
               
        # 格式转换
        iron_time['受铁开始时间'] = iron_time['受铁开始时间'].apply(
                                                                pd.to_datetime)
        iron_time['受铁结束时间'] = pd.to_datetime(iron_time['受铁结束时间'])  
        df_m = pd.merge(left=df, right=iron_time,left_index=True,
                                                right_on='铁次号')
        
        def foo(x):
            # 均摊函数, 当受铁时间段 跨越 6:00 12:00 18:00, 
            # 参考跨越时间段的前后比例, 按比例分配受铁重量
            t1, t2 = x['受铁开始时间'], x['受铁结束时间']
            t1, t2 = t1 - t1.floor('d'), t2 - t2.floor('d')
            
            t_6h = pd.to_timedelta("6h")
            t_12h = pd.to_timedelta("12h")
            t_18h = pd.to_timedelta("18h")
            
            if (t1 < t_6h and t_6h < t2):
                return (t_6h - t1) / (t2 - t1) * x['采集项值']
            elif (t1 < t_12h and t_12h < t2): 
                return (t_12h - t1) / (t2 - t1) * x['采集项值']
            elif (t1 < t_18h and t_18h < t2):    
                return (t_18h - t1) / (t2 - t1) * x['采集项值']
            else:
                return x['采集项值']
        
        df_m['start_value'] = df_m.apply(foo, axis=1) # 函数式编程
        df_m['end_value'] = df_m['采集项值'] - df_m['start_value']
        
        # 格式化结果 方便resample
        df_f1 = pd.DataFrame(data=df_m['start_value'].to_numpy(), 
                             index=df_m['受铁开始时间'],
                             columns =['采集项值'])
        df_f2 = pd.DataFrame(data=df_m['end_value'].to_numpy(), 
                             index=df_m['受铁结束时间'],
                             columns =['采集项值'])
        df_f = pd.concat([df_f1, df_f2])
        six = df_f.resample('6h').sum()
        self.res['日产量'] = six
        
        return None
    
    
    def get_ratio(self): 
        '''
        计算焦比, 煤比, 燃料比
        必须在计算日产量之后运行
        '''
        # 焦比
        df = pd.read_pickle('./pkl/上料实绩表.pkl')
        
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])   
        df1 = df.groupby('采集项名称').get_group('冶金焦（自产）')
        df2 = df.groupby('采集项名称').get_group('小块焦')[['业务处理时间','采集项值']]
        df1.set_index('业务处理时间', inplace=True) 
        df1.sort_index(inplace=True)
        df2.set_index('业务处理时间', inplace=True) 
        df2.sort_index(inplace=True)
        self.res['焦比'] = df1.resample('6h').sum() + df2.resample('6h').sum()
        self.res['焦比'] = self.res['焦比'] / self.res['日产量'] * 1e3
        
        # 煤比
        df = pd.read_pickle('./pkl/西昌2#高炉采集数据表_喷吹系统.pkl')
        
        df['采集项值'] = pd.to_numeric(df['采集项值']) # 格式化
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间']) # 格式化
        
        df = df.groupby('采集项名称').get_group('日喷煤量')[['业务处理时间','采集项值']]
        df = df.set_index('业务处理时间').sort_index()
        df['采集项值'][df['采集项值'] > 1e4] = None # 去除1e9
        df['diff'] = df.diff() # 差分
        
        # 日喷煤量初始化400变0情况的处理
        df['diff'][df['diff'] < -100] = df['采集项值'][df['diff'] < -100] 
      
        self.res['煤比'] = df['diff'].resample('6h').sum()[:'2019-11-07 6:00:00']
        self.res['煤比'] = self.res['煤比'] / self.res['日产量'] * 1e3
        # 燃料比
        self.res['燃料比'] = self.res['焦比'] + self.res['煤比']
        return None

    
    def get_molten_iron(self):
        """
        计算 [C] [Ti] [Si] [S] Delta[Ti]
        """
        df = pd.read_pickle('./pkl/铁水成分表.pkl')
        df = df[df['铁次号']>='20000000'] # 提取出#2高炉的数据
        df = df[df['铁次号']<'30000000']
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df['铁次号'] = pd.to_numeric(df['铁次号'])
        
        iron_time = pd.read_excel('铁次时间.xlsx')
        iron_time['受铁开始时间'] = pd.to_datetime(iron_time['受铁开始时间'])
        
        param_list = ['[C]', '[Ti]', '[Si]', '[S]']
        
        for param in param_list:
            df_C = df.groupby('采集项名称').get_group(param)[['铁次号','采集项值']]
            df_C = df_C.groupby('铁次号').mean()
            
            df_merge = pd.merge(left=df_C, right=iron_time, left_index=True,
                                right_on = '铁次号')
            df_C = df_merge[['受铁开始时间','采集项值']].set_index('受铁开始时间')
            
            if param == '[Ti]':
                self.res['Delta[Ti]'] = (df_C.resample('6h').apply(np.max) 
                                         - df_C.resample('6h').apply(np.min))
            
            self.res[param] = df_C.resample('6h').mean()
        return None

    
    def get_slag(self):
        """
        计算:
        R2,R3,TiO2,镁铝比,DeltaR2
        """
        # 数据读取与格式化
        df = pd.read_pickle('./pkl/'+'炉渣成分表'+'.pkl')
        df = df[df['铁次号']>='20000000'] # 提取出#2高炉的数据
        df = df[df['铁次号']<'30000000']
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df['铁次号'] = pd.to_numeric(df['铁次号'])
        # 数据读取与格式化
        iron_time = pd.read_excel('铁次时间.xlsx')
        iron_time['受铁开始时间'] = pd.to_datetime(iron_time['受铁开始时间'])
        
        param_list = [
            '(CaO)',
            '(SiO2)',
            '(MgO)',
            '(TiO2)',
            '(Al2O3)']
        
        delta = pd.DataFrame(data=None, index=iron_time['受铁开始时间'])
        
        for param in param_list:
            df_C = df.groupby('采集项名称').get_group(param)[['铁次号','采集项值']] # 筛选
            df_C = df_C.groupby('铁次号').mean() # 合并同铁次
            # 铁次号打上时间标记, 暂时标记为 开始时间
            df_merge = pd.merge(left=df_C, right=iron_time, left_index=True,
                                right_on = '铁次号')
            df_C = df_merge[['受铁开始时间','采集项值']].set_index('受铁开始时间')
            
            if param in ['(CaO)','(SiO2)']: # 保存原始的关于 R2的数据, 以便于计算DeltaR2
                delta[param] = df_C
           
            self.res[param] = df_C.resample('6h').mean()
        
        self.res['R2'] = self.res['(CaO)'] / self.res['(SiO2)']
        self.res['R3'] = (self.res['(CaO)'] + self.res['(MgO)']) / self.res['(SiO2)']
        self.res['美铝比'] = self.res['(MgO)'] / self.res['(Al2O3)']
    
        delta['R2'] = delta['(CaO)'] / delta['(SiO2)']
        self.res['DeltaR2'] = (delta['R2'].resample('6h').apply(np.max) 
                          - delta['R2'].resample('6h').apply(np.min))
        
        return None


    def get_coke(self):    
        """
        计算焦炭5个性能:
            M40: 焦炭粒度、冷强度_M40
            M10: 焦炭粒度、冷强度_M10
            CRI: 焦炭热性能_CRI
            CSR: 焦炭热性能_CSR
            S: 焦炭工分_St
        """
        df = pd.read_pickle('./pkl/上料质量表.pkl')
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        # df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        def foo(x):
            # 跑程序费时间
            # 191013D000402-2401 处理成 2019-10-14 00:01:00
            if x[-4:-2] != '24':
                return pd.to_datetime('20'+x[0:6]+x[-4:])
            else:
                return pd.to_datetime('20'+x[0:6]+'00'+x[-2:]) + pd.to_timedelta('1D')
                
        df['上料批号'] = df['上料批号'].apply(foo)
        param_dict = {'M40':'焦炭粒度、冷强度_M40',
                      'M10':'焦炭粒度、冷强度_M10',
                      'CRI':'焦炭热性能_CRI',
                      'CSR':'焦炭热性能_CSR',
                      'S':'焦炭工分_St'}
        for k, param in zip(param_dict.keys(), param_dict.values()):
            df_C = df.groupby('采集项名称').get_group(param)[['上料批号','采集项值']]
            self.res[k] = df_C.set_index('上料批号').resample('6h').mean()
        return None
    
if __name__ == "__main__":

    solv = Solution()

    solv.get_yield()
    solv.get_ratio()
    solv.get_molten_iron()
    solv.get_slag()
    solv.get_coke()
    res = solv.res
    
    # res即为所求
    