# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
'''
待补充
整理19年10月-20年2月数据
需要以下目录文件:
./data/西昌2#高炉数据19年10-11月/pkl/
    西昌2#高炉采集数据表_渣铁系统.pkl
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
        df = df[['业务处理时间','采集项值']]
        df = df.groupby('业务处理时间').sum()
        self.res['日产量'] = df['采集项值']        
            
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
    
if __name__ == '__main__':
    
    index = pd.date_range('2019-12-01 00:00:00', '2020-2-15 00:00:00', freq='1D')
    daily19 = DailyDate(index)
    
    daily19.get_yield(PATH_DICT[2]+'西昌2#高炉-铁水实绩表.pkl')
    daily19.get_coke(PATH_DICT[2]+'西昌2#高炉-上料质量表.pkl')
    daily19.get_molten_iron(PATH_DICT[2]+'西昌2#高炉-铁水成分表.pkl')
    res = daily19.res
    


    
      
 
