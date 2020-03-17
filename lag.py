"""
3月22日前搞出 滞后时间
画参数的曲线
画滞后取值曲线

"""

"""
时间滞后分析v5.0
计算控制参数与生产指标之间的时间滞后
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# 修补画图时 中文乱码的问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# excel 文件处理成 pkl文件后 的存放路径
PRE_PATH = {19: 'data/西昌2#高炉数据19年10-11月/pkl/',
            20: 'data/西昌2#高炉数据19年12月-20年2月/pkl/'}

# 铁次时间表的存放路径
IRON_TIME = {19: 'data/西昌2#高炉数据19年10-11月/铁次时间.xlsx',
             20: 'data/西昌2#高炉数据19年12月-20年2月/origin/铁次时间.xlsx'}

def find_table(name, table):
    """
    给出指标 自动寻找在那个表里
    :param name: 要寻找的指标名
    :param table 数据源选择 取值 19 或者 20
    :return 表名
    """
    if table == 19:
        path = 'data/19数据表各个名称罗列.xlsx'
    elif table == 20:
        path = 'data/20数据表各个名称罗列.xlsx'
    dic = pd.read_excel(path)
    temp = dic[dic.isin([name])].dropna(axis=1, how='all')
    if temp.values.shape[1] == 0:
        print("表:", table, "无", name, "!!!!")
        return None
    elif temp.values.shape[1] == 1:
        return temp.columns[0]
    elif temp.values.shape[1] > 1:
        print("表:", table, "有大于一个的", name, "自动返回发现的第一个")
        return temp.columns[0]
    
def get_df(param, table):
    """
    给出 dataframe 数据
    :param param: 指标名
    :param table: 19年 还是 20 年的表 
    :return:
    """
    table_name = find_table(param, table)
    path = PRE_PATH[table] + table_name + '.pkl'
    df = pd.read_pickle(path)
    
    # 为了去除冗余
    if '系统接收时间' in df.columns:
        df.drop(columns='系统接收时间', inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def process_time_data(params):
    """
    数据必须 有 有效的!! 业务处理时间!!
    
    收入指标名称 输出 整理好的一分钟频率采集的数据表
    
    在同一个pkl文件的处理
    
    """
    res = pd.DataFrame()
    
    # 19 20 年的数据都读取进来
    df19 = get_df(params[0], 19)
    df20 = get_df(params[0], 20)
    df = pd.concat([df19,df20]) 
    
    df['采集项值'] = pd.to_numeric(df['采集项值']) # 格式化
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间']) # 格式化
    df['采集项值'][df['采集项值']>1e7] = None # 去除 99999
    for param in params:
        grouped = df.groupby('采集项名称').get_group(param)
        grouped = grouped.set_index('业务处理时间')
        resampled = grouped.resample('1T').agg(np.mean).rename(columns={'采集项值':param}) # 重采样1min
        temp = resampled.interpolate() # 线性插值
        res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    return res

def get_time_table(table):
    """
    获取 铁次时间表的 DataFrame 型
    其中 index 是其 铁次
    :return:
    """
    time_table = pd.read_excel(IRON_TIME[table])

    # 格式化
    time_table['受铁开始时间'] = time_table['受铁开始时间'].astype('datetime64')
    time_table['受铁结束时间'] = time_table['受铁结束时间'].astype('datetime64')
    time_table['铁次号'] = time_table['铁次号'].astype('int64')

    # 提取出#2高炉的数据
    time_table = time_table[time_table['铁次号'] >= 20000000]
    time_table = time_table[time_table['铁次号'] < 30000000]
    time_table = time_table.set_index('铁次号').sort_index()

    return time_table

def process_iron_order_data(params):
    """
    处理铁次号型的数据
    """
    res = pd.DataFrame()
    df_iorn_time = pd.concat([get_time_table(19), get_time_table(20)])
    
    df = pd.concat([get_df(params[0],19), get_df(params[0],20)])
    df['铁次号'] = pd.to_numeric(df['铁次号'])
    df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化
    df = df[df['铁次号'] >= 20000000]  # 提取出#2高炉的数据
    df = df[df['铁次号'] < 30000000]
    
    for param in params:
    # param = params[0]
        grouped = df.groupby("采集项名称").get_group(param)
        grouped = grouped.groupby("铁次号").mean()
        # grouped_idx = grouped.set_index('铁次号').sort_index()
        merged = pd.merge(df_iorn_time['受铁开始时间'],grouped,how='outer',left_index=True,
                          right_index=True)
        merged = merged.rename(columns={'受铁开始时间':'业务处理时间'}).set_index('业务处理时间')
        resampled = merged.resample('1T').agg(np.mean).rename(columns={'采集项值':param}) # 重采样1min
        temp = resampled.interpolate() # 线性插值
        res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    # temp=process_time_data(params)
    return res

def get_datas():
    param_list = "热风温度 送风风量 热风压力 富氧量\
                  焦炭负荷 炉顶压力1 炉顶压力2\
                  炉腹煤气发生量  炉顶温度1  炉喉温度1 炉顶煤气CO  炉顶煤气CO2  \
                  喷吹速率 \
                  理论燃烧温度 鼓风动能\
                  [铁水温度] \
                  [Si] [Ti] [S] \
                  (CaO) (SiO2)   ".split()
    
    for item in param_list:
        print(find_table(item,19))
    
    res = pd.DataFrame()
    

    # 热风温度 送风风量 热风压力 富氧量
    params = "热风温度 送风风量 热风压力 富氧量 ".split()
    temp = process_time_data(params)
    res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    
    
    params = "焦炭负荷 炉顶压力1 炉顶压力2 ".split()
    temp = process_time_data(params)
    res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    luding_mean = res[['炉顶压力1','炉顶压力2']].mean(axis=1)
    #  透气性指数 = 送风风量/(热风压力-炉顶压力1-2) *100
    res['透气性指数'] = res['送风风量']/(res['热风压力']-luding_mean) *100
    
    # 炉腹煤气发生量  炉顶温度1  炉喉温度1 炉顶煤气CO  炉顶煤气CO2
    params = "炉腹煤气发生量  炉顶温度1  炉喉温度1 炉顶煤气CO  炉顶煤气CO2 \
        炉顶温度2 炉顶温度3 炉顶温度4 炉喉温度2 炉喉温度3 炉喉温度4 炉喉温度5\
        炉喉温度6 炉喉温度7 炉喉温度8".split()
    temp = process_time_data(params)
    res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    
    res['煤气利用率'] = res['炉顶煤气CO2']/(res['炉顶煤气CO']+res['炉顶煤气CO2'])
    res['炉顶温度(极差)'] = (res[['炉顶温度1','炉顶温度2','炉顶温度3','炉顶温度4']].max(axis=1) 
                          - res[['炉顶温度1','炉顶温度2','炉顶温度3','炉顶温度4']].min(axis=1))
    res['炉喉温度(极差)'] = (res[['炉喉温度1','炉喉温度2','炉喉温度3','炉喉温度4','炉喉温度5','炉喉温度6','炉喉温度7','炉喉温度8']].max(axis=1) 
                          - res[['炉喉温度1','炉喉温度2','炉喉温度3','炉喉温度4','炉喉温度5','炉喉温度6','炉喉温度7','炉喉温度8']].min(axis=1))
    
    params = "理论燃烧温度 鼓风动能".split()
    temp = process_time_data(params)
    res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    
    
    temp = process_time_data(['喷吹速率'])
    res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    
    
    params = "[Si] [Ti] [S]".split()
    temp = process_iron_order_data(params)
    res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    res['[Si]+[Ti]'] = res['[Si]'] + res['[Ti]']
    
    res['[铁水温度]'] = process_iron_order_data(['[铁水温度]'])
    
    params = "(CaO) (SiO2)".split()
    temp = process_iron_order_data(params)
    res = pd.merge(res,temp,how="outer",left_index=True,right_index=True)
    res['R2'] = res['(CaO)'] / res['(SiO2)']
    
    param_list = "40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()
    # temp = process_time_data(param_list)
    param = param_list[0]
    
    df19 = get_df(param_list[0], 19)
    df20 = get_df(param_list[0], 20)
    df = pd.concat([df19,df20]) 
    
    df['采集项值'] = pd.to_numeric(df['采集项值']) # 格式化
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间']) # 格式化
    df['采集项值'][df['采集项值']>1e7] = None # 去除 99999
    res_tmp = pd.DataFrame()
    for param in param_list:
        grouped = df.groupby('采集项名称').get_group(param)
        grouped = grouped.set_index('业务处理时间')
        resampled = grouped.resample('2h').agg(np.sum).rename(columns={'采集项值':param}) # 重采样1min
        res_tmp = pd.merge(res_tmp,resampled,how="outer",left_index=True,right_index=True)
    
    # 计算比例
    res_sum = res_tmp.sum(axis=1)
    for param in param_list:
        res_tmp[param] = res_tmp[param] / res_sum
    res = pd.merge(res,res_tmp,how="outer",left_index=True,right_index=True)
    
    # nan值填充
    for param in param_list:
        res[param] = res[param].ffill()
        
    return res

def lag_analys(i,j,lag_min,lag_max):
    """
    i: 控制参数的序号
    j: 生产参数的序号
    """
    ctrl = res[controls[i]]
    prod = res[products[j]]
    
    plt.figure()
    ctrl_std = (ctrl-ctrl.mean())/ctrl.std()
    ctrl_std['2020-02-01':'2020-02-02'].plot(label=controls[i])
    prod_std = (prod-prod.mean())/prod.std()
    prod_std['2020-02-01':'2020-02-02'].plot(label=products[j])
    plt.title("{}与{}的波动图(未滞后处理)".format(products[j],controls[i]))
    plt.xlabel("正态标准化数值")
    plt.legend()
    
    
    plt.savefig('img/滞后/'+"{}与{}的波动图(未滞后处理)".format(products[j],controls[i]))
    plt.close()
    
    ##  滞后图
    
    corr_list=[]
    for periods in range(lag_min*60,lag_max*60+1):
        corr_list.append(ctrl.shift(periods).corr(prod))
    
    plt.figure()
    plt.plot(range(lag_min*60,lag_max*60+1), np.abs(corr_list))
    plt.xlabel("滞后时间/min")
    plt.ylabel("绝对相关系数")
    np_corr_list = np.abs(np.array(corr_list))
    
    lag_time = np_corr_list.argmax()+lag_min*60
    plt.scatter(lag_time,np_corr_list.max(),c='r')
    
    
    plt.title("{}与{}的滞后时间分析图(滞后结果:{}min)".format(products[j],controls[i],lag_time))

    
    print("{}与{}的滞后时间分析图(滞后结果:{}min)".format(products[j],controls[i],lag_time))
    plt.savefig('img/滞后/'+"{}与{}的滞后时间分析图".format(products[j],controls[i],lag_time))
    plt.close()
    
    
    
    ## 滞后处理后的图
    fig_name3 = "{}与{}的波动图(滞后处理后)".format(products[j],controls[i])
    plt.figure()
    ctrl_std['2020-02-01':'2020-02-02'].shift(lag_time).plot(label=controls[i])
    prod_std['2020-02-01':'2020-02-02'].plot(label=products[j])
    plt.title(fig_name3)
    plt.xlabel("正态标准化数值")
    
    plt.legend()
    plt.savefig('img/滞后/'+fig_name3)
    plt.close()
    return lag_time

if __name__ == "__main__":
    res = get_datas()    
    controls = "热风温度 送风风量 热风压力 富氧量 喷吹速率 鼓风动能\
        40赤块 冶金焦（自产） 南非块矿 小块焦 烧结矿 白马球团 酸性烧结矿".split()
    # products = "焦炭负荷 透气性指数 炉腹煤气发生量 理论燃烧温度 炉顶温度(极差) \
    #             炉喉温度(极差) 煤气利用率 [铁水温度] [Si]+[Ti] [S] R2".split()
    tbl ="焦炭负荷         4  6 \
        透气性指数         0  6 \
        炉腹煤气发生量     0  6 \
        理论燃烧温度       0  6 \
        炉顶温度(极差)     0  6 \
        炉喉温度(极差)     0  6  \
        煤气利用率         0  6 \
        [铁水温度]         4  6 \
        [Si]+[Ti]         4  6 \
        [S]               4  6 \
        R2                4  6 ".split()
    prod_min = [int(item) for item in tbl[1::3]]
    prod_max = [int(item) for item in tbl[2::3]]
    products = tbl[0::3]
    ## 未处理滞后的图
    # i, j = 0, 0
    # lag_min = 4
    # lag_max = 6
    # lag(i,j,lag_min,lag_max)

    lag_res_table = pd.DataFrame(data=0,index=controls,columns=products)
    for j in range(len(products)):
        lag_min = prod_min[j]
        lag_max = prod_max[j]
        for i in range(len(controls)):
            lag_res_table.loc[controls[i], products[j]] = lag_analys(i,j,lag_min,lag_max)
    
    lag_res_table.to_excel('滞后结果表.xlsx')
    
    
    