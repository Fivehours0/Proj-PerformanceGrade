# -*- coding: utf-8 -*-
"""
v2.1 更新说明
补充 探尺差, 实际风速, 炉腹煤气指数等

"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
'''

整理19年10月-20年2月数据
需要以下目录文件:
./data/西昌2#高炉数据19年10-11月/pkl/
    西昌2#高炉采集数据表_送风系统.pkl
    西昌2#高炉采集数据表_喷吹系统.pkl
    铁水实绩表.pkl
    上料实绩表.pkl
    铁水成分表.pkl
    炉渣成分表.pkl
    上料质量表.pkl
./data/西昌2#高炉数据19年10-11月/    
    铁次时间.xlsx
./data/西昌2#高炉数据19年12月-20年2月/origin/
    铁次时间.xlsx
./data/西昌2#高炉数据19年12月-20年2月/pkl/
    西昌2#高炉采集数据表_送风系统.pkl
    西昌2#高炉采集数据表_喷吹系统.pkl
    西昌2#高炉-炉渣成分表.pkl   
    西昌2#高炉-上料实绩表.pkl
    西昌2#高炉-上料质量表.pkl
    西昌2#高炉-铁水实绩表.pkl
    西昌2#高炉-铁水成分表.pkl
'''

PATH_DICT = {    
0:'./data/西昌2#高炉数据19年10-11月/pkl/',
1:'./data/西昌2#高炉数据19年10-11月/',
2:'./data/西昌2#高炉数据19年12月-20年2月/pkl/',
3:'./data/西昌2#高炉数据19年12月-20年2月/origin/ '}

class DailyDate():
    
    def __init__(self, index):
        '''
        Parameters
        ----------
        index : pd.date_range
            时间数组
            
        Returns
        -------
        None.
        '''
        self.res = pd.DataFrame(data=None,index=index)
        return None
    
    def get_yield(self, file_pkl):
        '''   
        Parameters
        ----------
        file_pkl : TYPE str
            铁水实绩表 pkl 文件路径
        Returns
        -------
        None.

        '''
        df = pd.read_pickle(file_pkl)
        # 格式转换   
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df1 = df[['业务处理时间','采集项值','铁次号','罐号']].set_index('业务处理时间')
        df2 = df1.drop_duplicates() # 去除重复数据
        df3 = df2.groupby('业务处理时间').sum()
        self.res['日产量'] = df3['采集项值']    
        return None
    
    def get_coke(self, file_pkl):
        '''   
        Parameters
        ----------
        file_pkl : TYPE str
            西昌2#高炉-上料质量表 pkl 文件路径
        Returns
        -------
        None.

        '''        
        param_list = [
            '焦炭粒度、冷强度_M40',
            '焦炭粒度、冷强度_M10',
            '焦炭工分_St',
            '焦炭热性能_CRI',
            '焦炭热性能_CSR']
        
        df = pd.read_pickle(file_pkl)
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param)  
            temp1 = temp.groupby('业务处理时间').mean()
            self.res[param] = temp1['采集项值'].copy()
        return None
    
    def get_molten_iron(self, file_pkl):    
        '''
        Parameters
        ----------
        file_pkl : TYPE str
            西昌2#高炉-铁水成分表.pkl 文件路径
        Returns
        -------
        None.

        '''           
        param_list = [
                '[C]',
                '[Ti]',
                '[Si]',
                '[S]'] # 还有 Delta[Ti]

        df_iron_comp = pd.read_pickle(file_pkl)
        df_iron_comp = df_iron_comp[df_iron_comp['铁次号']>='20000000'] # 提取出#2高炉的数据
        df_iron_comp = df_iron_comp[df_iron_comp['铁次号']<'30000000']
        df = df_iron_comp
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param)
            temp = temp[['业务处理时间','采集项值']]
            temp1 = temp.groupby('业务处理时间').mean()
            if param == '[Ti]':
                self.res['Delta[Ti]'] =( temp.groupby('业务处理时间')['采集项值'].apply(np.max) - 
                                   temp.groupby('业务处理时间')['采集项值'].apply(np.min) )
            self.res[param] = temp1['采集项值'].copy()    
        return None
    
    def get_slag(self, file_pkl):
        '''
        Parameters
        ----------
        file_pkl : TYPE str
             西昌2#高炉-炉渣成分表.pkl 文件路径
        Returns
        -------
        None.

        '''
        df_slag = pd.read_pickle(file_pkl)
        df_slag = df_slag[df_slag['铁次号']>='20000000'] # 提取出#2高炉的数据
        df_slag = df_slag[df_slag['铁次号']<'30000000']    
        df = df_slag
        
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        
        param_list = [
                '(CaO)',
                '(SiO2)',
                '(MgO)',
                '(TiO2)',
                '(Al2O3)']
    
        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param)  
            temp1 = temp.groupby('业务处理时间').mean()
    
            self.res[param] = temp1['采集项值'].copy()
        
        self.res['R2'] = self.res['(CaO)']/self.res['(SiO2)']
        self.res['R3'] = (self.res['(CaO)'] + self.res['(MgO)']) / self.res['(SiO2)']
        self.res['镁铝比'] =  self.res['(MgO)']/self.res['(Al2O3)']
        
        
        # DeltaR2处理
        CaO = df.groupby('采集项名称').get_group('(CaO)') # 筛选
        CaO2 = CaO.groupby(['铁次号','业务处理时间'], as_index=False).mean().set_index('铁次号')
        
        SiO = df.groupby('采集项名称').get_group('(SiO2)') # 筛选
        SiO2 = SiO.groupby('铁次号').mean()
        
        CaO2['SiO2'] = SiO2['采集项值']
        CaO2['R2'] = CaO2['采集项值'] / CaO2['SiO2']
        self.res['DeltaR2'] = CaO2.groupby('业务处理时间')['R2'].mean()        
        return None
    
    def get_ratio(self, file_pkl1, file_pkl2):
        '''
        Parameters
        ----------
        file_pkl1 : TYPE str
             上料实绩表 文件路径
        file_pkl2 : TYPE str
             西昌2#高炉采集数据表_喷吹系统 文件路径
        Returns
        -------
        None.

        '''    
        ### 焦比
        df = pd.read_pickle(file_pkl1)
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间']).dt.floor('d')
        
        df_dict = {}
        for param in ['冶金焦（自产）', '小块焦']:    
            df1 = df.groupby('采集项名称').get_group(param)
            df1_1 = df1[['业务处理时间','采集项值','上料批号']].set_index('业务处理时间')
            df1_2 = df1_1.drop_duplicates() # 去除重复数据
            df1_3 = df1_2.groupby('业务处理时间').sum()['采集项值']
            df_dict[param] = df1_3
                        
        self.res['焦比'] = df_dict['冶金焦（自产）'] + df_dict['小块焦']
        self.res['焦比'] = self.res['焦比'] / self.res['日产量'] * 1000
               
        # #  煤比  
        # 喷吹速率
        df = pd.read_pickle(file_pkl2)    
        df['采集项值'] = pd.to_numeric(df['采集项值']) # 格式化
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间']) # 格式化
        df = df.groupby('采集项名称').get_group('喷吹速率')[['业务处理时间','采集项值']]
        df = df.set_index('业务处理时间').sort_index()
        df['采集项值'][df['采集项值'] > 1e4] = None # 去除1e9
        df_1T = df.resample('1T').mean()
        df_1T = df_1T.interpolate(method='linear')
        daily = df_1T.resample('1D').sum()
        self.res['煤比'] = daily.采集项值 / self.res.日产量 * 20
        
        self.res['燃料比'] = self.res['焦比'] + self.res['煤比']
        return None
    
    def get_wind(self, file_pkl):
        '''        
        file_pkl1 : TYPE str
             西昌2#高炉采集数据表_送风系统 文件路径
             
        '标准风速'
        '西昌2#高炉采集数据表_送风系统'
        
        实际风速=标准风速*(0.101325/273)*((273+风温)/(风压/10+0.101325))
        
        标准风速 245   m3/s   标准风速
        风温    1212  摄氏度	 热风温度
        风压    3.45  0.1MPa	 热风压力
        
        18年的实际风速平均 298
        '''
        # path = PATH_DICT[0] 
        # file = '西昌2#高炉采集数据表_送风系统.pkl'
        df = pd.read_pickle(file_pkl)
        
        # 格式化
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
        
        res = []
        param_list = ['标准风速', '热风温度', '热风压力']
        for param in param_list:
            temp = df.groupby('采集项名称').get_group(param).set_index('业务处理时间')    
            temp.rename(columns={'采集项值':param}, inplace=True)
            temp[param][temp[param] > 1e7] = None
            res.append(temp.resample('24h').mean())
        cat = pd.concat(res, axis=1)
          
        cat['实际风速'] = cat['标准风速']*(0.101325/273)*((273+cat['热风温度'])/(cat['热风压力']/1000+0.101325))
        self.res['实际风速'] = cat['实际风速']

        return None

    def get_rod_range(self, file_pkl):
        """
        计算探尺差
        探尺差
        西昌2#高炉采集数据表_上料系统
        """
        df = pd.read_pickle(file_pkl) # 导入
        
        # 格式化
        df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df['采集项值'] = pd.to_numeric(df['采集项值'])
           
        # 把三个探尺高度筛选出来
        brothel = ['探尺（南）','探尺（东）','探尺（西）']
        hookers = []
        for hooker_name in brothel:
            hooker = df.groupby('采集项名称').get_group(hooker_name).set_index('业务处理时间') # 筛选
            hooker.drop(columns=['采集项编码','采集项名称'], inplace=True) 
            hooker.rename(columns={'采集项值':hooker_name}, inplace=True)
    
            hooker[hooker_name][hooker[hooker_name] > 1e7] = None # 去除1e7 的异常值
            hooker[hooker_name].drop_duplicates(keep=False, inplace=True) # 去除数据源中同一时刻的重复采样
            hookers.append(hooker)
        
        # 找出 所有 在同一时刻 三个探尺高度数据都不缺失的样本
        temp = pd.merge(hookers[0], hookers[1], how="inner", left_index=True, right_index=True)
        blondie = pd.merge(temp, hookers[2], how="inner", left_index=True, right_index=True)
        # 计算极差
        blondie['探尺差'] = blondie.max(axis=1) - blondie.min(axis=1)
        # 日平均
        wife = blondie['探尺差'].resample("24h").mean()
        self.res['探尺差'] = wife        
        return None
    
    def get_gas(self, file_pkl):
        '''
        炉腹煤气指数计算:
            
        炉腹煤气发生量/(9.5*9.5*3.14/4)
        
        文件名:
        西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹)
        '''
        
        df = pd.read_pickle(file_pkl)
        df = df.groupby("采集项名称").get_group('炉腹煤气发生量')
        
        # 格式化
        df.loc[:,'业务处理时间'] = pd.to_datetime(df['业务处理时间'])
        df.loc[:,'采集项值'] = pd.to_numeric(df['采集项值'])
        df.set_index('业务处理时间', inplace=True)
        df['采集项值'][df['采集项值'] > 1e7] = None
        taylor = df.resample("24h").mean()
        self.res['炉腹煤气指数'] = taylor /(9.5*9.5*3.14/4)        
        
        return None
    
def main():
    index20 = pd.date_range('2019-12-01 00:00:00', '2020-2-15 00:00:00', freq='1D')
    daily20 = DailyDate(index20)
    
    index19 = pd.date_range('2019-10-01 00:00:00', '2019-11-30 23:59:59', freq='1D')
    daily19 = DailyDate(index19)
    
    daily20.get_yield(PATH_DICT[2]+'西昌2#高炉-铁水实绩表.pkl')
    daily20.get_coke(PATH_DICT[2]+'西昌2#高炉-上料质量表.pkl')
    daily20.get_molten_iron(PATH_DICT[2]+'西昌2#高炉-铁水成分表.pkl')
    daily20.get_slag(PATH_DICT[2]+'西昌2#高炉-炉渣成分表.pkl')
    daily20.get_ratio(PATH_DICT[2]+'西昌2#高炉-上料实绩表.pkl', PATH_DICT[2]+'西昌2#高炉采集数据表_喷吹系统.pkl')
    daily20.get_wind(PATH_DICT[2]+'西昌2#高炉采集数据表_送风系统.pkl')
    daily20.get_rod_range(PATH_DICT[2]+'西昌2#高炉采集数据表_上料系统.pkl')
    
    daily19.get_yield(PATH_DICT[0]+'铁水实绩表.pkl')
    daily19.get_coke(PATH_DICT[0]+'上料质量表.pkl')
    daily19.get_molten_iron(PATH_DICT[0]+'铁水成分表.pkl')
    daily19.get_slag(PATH_DICT[0]+'炉渣成分表.pkl')
    daily19.get_ratio(PATH_DICT[0]+'上料实绩表.pkl', PATH_DICT[0]+'西昌2#高炉采集数据表_喷吹系统.pkl')
    daily19.get_wind(PATH_DICT[0]+'西昌2#高炉采集数据表_送风系统.pkl')
    daily19.get_rod_range(PATH_DICT[0]+'西昌2#高炉采集数据表_上料系统.pkl')
    
    daily19.get_gas(PATH_DICT[0]+'西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl')
    daily20.get_gas(PATH_DICT[2]+'西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl')
    
    res = pd.concat([daily19.res, daily20.res])
    return res
    
if __name__ == '__main__':
    
    # 各个指标的处理说明
    # https://docs.qq.com/sheet/DTnRobmxQbUxIUU9a?tab=5u26wg&c=A1A0A0
    
    
    
    res = main()
    
    # index20 = pd.date_range('2019-12-01 00:00:00', '2020-2-15 00:00:00', freq='1D')
    # daily20 = DailyDate(index20)
    
    # index19 = pd.date_range('2019-10-01 00:00:00', '2019-11-30 23:59:59', freq='1D')
    # daily19 = DailyDate(index19)    
    
    
    # daily19.get_gas(PATH_DICT[0]+'西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl')
    # daily20.get_gas(PATH_DICT[2]+'西昌2#高炉采集数据表_高炉本体(炉顶,炉喉,炉身,炉腹).pkl')
    
    # res = pd.concat([daily19.res, daily20.res])
    
    
    
    
    
    
    
    
    
    
    
    
    
    