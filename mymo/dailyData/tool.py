import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def readSheet(path):
    """    
    function: 合并文件中的多个sheet ###
    path： 需要处理的excel文件名称
    return: 返回合并好后的数据，格式为dataFrame"""
    df = pd.read_excel(path, sheet_name=None) # 读表
    sheetNames = list(df.keys()) # sheet表的名称 
    columns = list(df[sheetNames[0]].columns) # 数据的columns
    sheetNum = len(sheetNames) # sheet表的个数
    dfAll = pd.DataFrame(data=None, index=None, columns=columns)
    for i in range(sheetNum):
        appendData = df[sheetNames[i]]
        if appendData.empty==False:
            appendData.columns = columns
            dfAll = dfAll.append(appendData, sort=False)
    dfAll.index =  range(dfAll.shape[0])
    return dfAll


def dealDataWithDealtime(df):
    """    
    function: 读取业务处理时间有效的数据并按照业务处理时间排序 ###
    df: 表格读入的数据
    return: storeSplitData:数据格式为字典，key为采集项名称，value为dataframe(index为业务处理时间, data为采集项值)"""
    split_sort = df.set_index(['采集项名称', '业务处理时间']).sort_index(level=['采集项名称', '业务处理时间'])
    split_sort['采集项值'].replace([999999999.0000001, np.nan], inplace=True)# 将异常值替换为nan

    storeSplitData = {} # 创建一个字典用以保存分割后的数据
    splitDataKeys = split_sort.index.levels[0] # 字典的key，即保存分割数据的名称

    for i in range(splitDataKeys.shape[0]): # 分割数据,保存至字典
        storeSplitData[splitDataKeys[i]] = split_sort.loc[split_sort.index.levels[0][i], '采集项值']
    return storeSplitData


def decreaseSampleFreq(data, freq):
    """   
    function: 降低数据的采样频率
    data: 输入的数据，数据格式为:index为业务处理时间，value为采集项值。如2019-11-30 23:56:35    382.85828
    freq: 新的采样时间间隔
    return: 返回新采样频率的数据，数据格式为DataFrame"""
    resampleDate = pd.to_datetime(data.index) # 将Index转换为DatetimeIndex格式
    newData = data.copy()
    newData.index = resampleDate
    newData = newData.resample(freq).mean() # 降采样，降低采样频率
    return newData


def lateAnalysis(data1, data2, lengh=70):
    """    
    function: 降低数据的采样频率
    data1: 输入的数据，数据格式为:index为业务处理时间，value为采集项值。如2019-11-30 23:56:35    382.85828
    data2: 新的采样时间间隔
    lengh: 新的采样时间间隔
    return: 返回新采样频率的数据，数据格式为DataFrame"""
    corrList = [] # 存储不同时滞下的相关系数
    corrList.append(data1.corr(data2)) # 因为-0返回的是空
    for i in range(1, lengh):
        corrList.append(data1[i: ].corr(data2[: -i])) # 位移信号
    return corrList



def calTimeInterval(data1, data2):
    """
    function: 计算两个时间序列的差值, data2 - data1
    data1: 数据类型：series 输入的数据
    data2: 数据类型：series 输入的数据
    return: 时间间隔列表"""
    return pd.to_datetime(data2) - pd.to_datetime(data1)


def deleteErrorData(data1, times):
    """    
    function: 删除值较高异常点
    data1: 数据类型：series 输入的数据
    times: 数据类型：int 大于均值times倍的数据将会被剔除
    return: 异常点剔除后的Series"""
    index = data1.index
    meanValue = data1.mean()
    data1 = np.where(data1 > meanValue * 2, np.nan, data1)
    data1 = pd.Series(data1, index=index)
    data1.fillna(data1.mean(), inplace=True)
    return data1


def comparaTime(ironTime, data):
    """ 
    function：将某个指标的每一条数据，用其业务处理时间所处的相应的铁次号(label)进行标记
    parameter:
	    ironTime 整个铁次时间(铁次开始时间和结束时间) ，类型：dataframe
	    data 数据(业务处理时间和采集项值)，类型：dataframe
    return:
        resultDict 类型: 字典 数据以及数据对应的铁次号"""
    dataArray = [] # 在出铁开始-结束时间段内的数据，与铁次号数组一一对应，长度相同
    ironNumber = [] # 在出铁开始-结束时间段内的数据所对应的铁次号
    for i in range(ironTime.shape[0]):  
        ironNum = ironTime.iloc[i][0] # 铁次号
        ironStartTime = pd.to_datetime(ironTime.iloc[i][1]) # 受铁开始时间
        ironEndTime = pd.to_datetime(ironTime.iloc[i][2]) # 受铁结束时间
        dealTime = pd.to_datetime(data.index) # 业务处理时间
        value = data.values[(dealTime > ironStartTime) & (dealTime < ironEndTime)]
        if value.size == 0:
            ironNumber.extend([ironNum])
            dataArray.append(np.nan)
        else:
            ironNumber.extend([ironNum] * value.size)
            dataArray.extend(value)
    resultDict = {'数据': dataArray, '铁次': ironNumber}
    return resultDict 

def drawContrast(paraNeedDeal, data1, data2):
    for value in paraNeedDeal:
        # savePath = 'D:\\高炉项目\\program\\处理结果\\离群点\\' + value + '.png'
        plt.figure()
        ax1 = plt.subplot(1, 2, 1)
        ax1.set_title('均匀插值')
        ax1.set_xlabel('铁次号')
        ax1.set_ylabel(value)
        plt.scatter(data1[value].index, data1[value].values)

        ax1Ylim = list(ax1.get_ylim()) # 保持两幅图的纵坐标轴相同

        ax2 = plt.subplot(1, 2, 2)
        ax2.set_ylim(ax1Ylim[0], ax1Ylim[1])
        ax2.set_title('线性插值')
        ax2.set_xlabel('铁次号')
        ax2.set_ylabel(value)
        plt.scatter(data2.index, data2.values)
        # plt.savefig(savePath)
        plt.show()

        plt.close()
