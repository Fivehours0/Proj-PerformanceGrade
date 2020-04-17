# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
'''

整理19年10月-20年2月数据
需要以下目录文件:
./data/西昌2#高炉数据19年10-11月/pkl/
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
    
def main():
    index = pd.date_range('2019-12-01 00:00:00', '2020-2-15 00:00:00', freq='1D')
    daily20 = DailyDate(index)
    daily20.get_yield(PATH_DICT[2]+'西昌2#高炉-铁水实绩表.pkl')
    daily20.get_coke(PATH_DICT[2]+'西昌2#高炉-上料质量表.pkl')
    daily20.get_molten_iron(PATH_DICT[2]+'西昌2#高炉-铁水成分表.pkl')
    daily20.get_slag(PATH_DICT[2]+'西昌2#高炉-炉渣成分表.pkl')
    daily20.get_ratio(PATH_DICT[2]+'西昌2#高炉-上料实绩表.pkl', PATH_DICT[2]+'西昌2#高炉采集数据表_喷吹系统.pkl')
    
    index = pd.date_range('2019-10-01 00:00:00', '2019-11-30 23:59:59', freq='1D')
    daily19 = DailyDate(index)
    daily19.get_yield(PATH_DICT[0]+'铁水实绩表.pkl')
    daily19.get_coke(PATH_DICT[0]+'上料质量表.pkl')
    daily19.get_molten_iron(PATH_DICT[0]+'铁水成分表.pkl')
    daily19.get_slag(PATH_DICT[0]+'炉渣成分表.pkl')
    daily19.get_ratio(PATH_DICT[0]+'上料实绩表.pkl', PATH_DICT[0]+'西昌2#高炉采集数据表_喷吹系统.pkl')

    res = pd.concat([daily19.res, daily20.res])
    return res
    
if __name__ == '__main__':
    res = main()
    
    # 因为重复采集
    # 删除 DeltaR2,R2,R3,TiO2,,煤铝比 19-12-27的数据
    
    
    
    
    # file_pkl=PATH_DICT[0]+'炉渣成分表.pkl'
    # index = pd.date_range('2019-10-01 00:00:00', '2019-11-30 23:59:59', freq='1D')
    # res = pd.DataFrame(data=None,index=index)
    
    # df_slag = pd.read_pickle(file_pkl)
    # df_slag = df_slag[df_slag['铁次号']>='20000000'] # 提取出#2高炉的数据
    # df_slag = df_slag[df_slag['铁次号']<'30000000']    
    # df = df_slag    
    # df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
    # df['采集项值'] = pd.to_numeric(df['采集项值'])
    
    # # DeltaR2处理
    # CaO = df.groupby('采集项名称').get_group('(CaO)') # 筛选
    # CaO2 = CaO.groupby(['铁次号','业务处理时间'], as_index=False).mean().set_index('铁次号')
    
    # SiO = df.groupby('采集项名称').get_group('(SiO2)') # 筛选
    # SiO2 = SiO.groupby('铁次号').mean()
    
    # CaO2['SiO2'] = SiO2['采集项值']
    # CaO2['R2'] = CaO2['采集项值'] / CaO2['SiO2']
    # res['DeltaR2'] = CaO2.groupby('业务处理时间')['R2'].mean()    
    
    
    
    


    

    
      
 
