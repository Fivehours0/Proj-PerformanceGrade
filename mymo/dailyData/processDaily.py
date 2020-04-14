import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import tool 

plt.rcParams['font.sans-serif'] = ['SimHei']  #显示中文
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

PRE_PATH = 'data/西昌2#高炉数据20年2月-20年4月/pkl/'
# 铁次时间表的存放路径
IRON_TIME = 'data/西昌2#高炉数据20年2月-20年4月/origin/铁次时间.xlsx'

def find_table(name: str) -> str or None:
    """
    给出指标 自动寻找在那个表里
    :param name: 要寻找的指标名
    :param table 数据源选择 取值 19 或者 20
    :return 表名
    """
    path = 'data/20数据表各个名称罗列.xlsx'

    dic = pd.read_excel(path)
    temp = dic[dic.isin([name])].dropna(axis=1, how='all')
    if temp.values.shape[1] == 0:
        print("无", name, "!!!!")
        return None
    elif temp.values.shape[1] == 1:
        return temp.columns[0]
    elif temp.values.shape[1] > 1:
        print("有大于一个的", name, "自动返回发现的第一个")
        return temp.columns[0]

def get_df(param: str):
    """
    给出 dataframe 数据
    :param param: 指标名
    :param table: 19年 还是 20 年的表
    :return:
    """

    table_name = find_table(param)
    path = PRE_PATH + table_name + '.pkl'
    df = pd.read_pickle(path)

    # 为了去除冗余
    if '系统接收时间' in df.columns:
        df.drop(columns='系统接收时间', inplace=True)
    df.drop_duplicates(inplace=True)

    return df

class Solution:
    def __init__(self):
        """
        初始化
        """
        self.res = pd.DataFrame()

    def decreaseSampleFreq(self, data, freq):
        """   
        function: 降低数据的采样频率
        data: 输入的数据，数据格式为:index为业务处理时间，value为采集项值。如2019-11-30 23:56:35    382.85828
        freq: 新的采样时间间隔
        return: 返回新采样频率的数据，数据格式为DataFrame
        """
        resampleDate = pd.to_datetime(data.index) # 将Index转换为DatetimeIndex格式
        newData = data.copy()
        newData.index = resampleDate
        newData = newData.resample(freq).mean() # 降采样，降低采样频率
        return newData

    def get_df(self, param):
        """
        给出 dataframe 数据
        :param param: 指标名
        :return:
        """
        return get_df(param)  # df

    def process_business_time(self, df, param_list, range_flag=False, agg_func=np.mean):
        """
        对业务处理时间型数据 预处理
        读入数据 -> 铁次时间标定 -> 处理 -> 输出
        :param df: 要传入的表
        :param param_list: 要处理的指标列表 类型: list
        :param range_flag: 是否处理极差数据 类型: bool
        :param agg_func: 聚合方式 类型: 函数, 例如np.mean
        :return:
        """
        res = pd.DataFrame()
        for param in param_list:
            if not any(df["采集项名称"].isin([param])):
                raise KeyError("df 中 没有 param", df.shape, param)
            df_pure = df.groupby("采集项名称").get_group(param).rename(columns={'采集项值': param})  # 筛选 都在同一个表里
            df_pure[param] = pd.to_numeric(df_pure[param])
            df_pure[param].where(df_pure[param]<1e6, np.nan, inplace=True) # 去除 999999 的异常值
            if range_flag == False:
                df_pure = df_pure[['业务处理时间', param]].set_index('业务处理时间')
                df_pure = self.decreaseSampleFreq(df_pure, '1D')
            else:
                df_pure_max = df_pure[param].groupby(df_pure['铁次号']).max() # 得出每个铁次号中值的最大值
                df_pure_min = df_pure[param].groupby(df_pure['铁次号']).min() # 得出每个铁次号中值的最小值
                df_pure = df_pure_max - df_pure_min
                df_pure[df_pure==0] = np.nan # 将极差为0的数据置为空值

            res = pd.merge(res, df_pure, how="outer", left_index=True, right_index=True)
        return res    

    def ironWeight(self):
        """
        铁水实绩表
        铁水重量
        """
        param_list = ['受铁重量']
        df = self.get_df(param_list[0])
        res = self.process_business_time(df, param_list, agg_func = np.sum)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res
    
    def loading(self):
        """
        上料系统
        焦炭负荷 炉顶压力(计算透气性指数)
        """
        param_list = ['焦炭负荷', '炉顶压力1', '炉顶压力2']
        df = self.get_df(param_list[0])
        res = self.process_business_time(df, param_list)
        res['炉顶压力'] = res[['炉顶压力1', '炉顶压力2']].mean(axis=1)

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res

    def wind(self):
        """
        送风系统
        送风风量 热风压力(计算透气性指数)
        """
        param_list = ['送风风量', '热风压力']
        df = self.get_df(param_list[0])
        res = self.process_business_time(df, param_list)
        res['透气性指数'] = res['送风风量'] * 100 / (res['送风风量'] - self.res['炉顶压力'])

        self.res = pd.merge(self.res, res, how="outer", left_index=True, right_index=True)
        return res
        
    def get_noumenon1(self):
        """
        高炉本体1
        送风风量 热风压力(计算透气性指数)
        """       
        
def main():
    obj = Solution()

    obj.ironWeight()
    obj.loading()
    obj.wind()

    ans = obj.res
    ans[ans == np.inf] = np.nan  # 因为有些铁次铁量为0 从而导致一些煤比 焦比等铁量衍生指标 算出 inf, np.nan填充
    ans.to_excel("data/每日结果_无滞后处理.xlsx")  # 因为铁次产量为0 搞出不少 inf
    return ans

if __name__ == "__main__":
    ans = main()