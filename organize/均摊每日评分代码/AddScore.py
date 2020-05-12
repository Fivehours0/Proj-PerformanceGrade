"""
:describe: 为铁次数据增加系统评分和现场评分, 也可给分数添加标签
:author 杜智辉
"""
import pandas as pd
import numpy as np


class DataProcess:
    def __init__(self, ironData, ironTime, scoreData, scoreRange=None, tangJueLabel=None, interp=False, save=False,
                 savePath=None):
        '''
        Parameters
        ----------
            ironData: 铁次数据 类型: DataFrame or Series, index为铁次号
            tangJueLabel: 唐珏老师标签数据 类型: DataFrame or Series, index为铁次号
            ironTime: 受铁开始时间和结束时间 类型: DataFrame or Series, index为铁次号
            scoreData: 系统评分和现场评分数据 类型: DataFrame or Series, index为日期(格式: 年月日)
            scoreRange: 用于分数聚类的分数范围 类型: list, [0]位置为最大值 例如[100, 85, 75, 0]
            interp: 是否需要进行插值 类型: boolean
        '''
        self.ironData = ironData
        self.interp = interp
        self.tangJueLabel = tangJueLabel['标签']
        self.ironTime = ironTime
        self.scoreData = scoreData
        self.scoreRange = scoreRange
        self.save = save
        self.savePath = savePath

    def addIronTime(self, data, ironTime):
        '''
        去掉ironTime(受铁开始时间/受铁结束时间)的时分秒, 添加到data中, 用以添加评分, 最后会删除
        因为评分表是以日期为参照的, 所以需要添加该列作为对照

        Parameters
        ----------
            data: 待添加时间列的数据 类型: dataframe, index为铁次号
            ironTime: 铁次时间数据 类型: Series, index为铁次号
        Return
        ------
            类型: dataframe, 在data中添加一列时间(格式: 年月日)数据
        '''
        ironTime = pd.to_datetime(ironTime).dt.floor('d').rename('铁次时间')
        data = pd.merge(data, ironTime, how='left', left_index=True, right_index=True)
        return data

    def interpolate(self, ironData):
        '''
        对data先进行前向填充，后进行后向填充

        Parameters
        ----------
            data: 带填充的数据 类型: DataFrame or Series
        Return
        ------
            ironData: 填充完成的数据 类型: DataFrame or Series
        '''
        ironData.ffill(inplace=True)
        ironData.bfill(inplace=True)
        return ironData

    def scoreCalibration(self, data, score):
        '''
        为每一个样本添加系统评分，现场评分数据

        Parameters
        ----------
            data: 待标定得分的数据 类型: dataframe, 列数据包含铁次时间(列名称: 铁次时间，格式: 年月日)数据
            score: 分数数据表 类型: dataframe, index为时间(格式: 年月日)数据, 列数据包含系统评分和现场评分
        Return
        ------ 
            类型: dataframe, 在data中添加了列数据(系统评分列，现场评分列)
        '''
        scoreDict = {'铁次': [], '系统评分': [], '现场评分': []}
        for value in score.index:  # 对系统和现场评分表的时间进行循环
            count = sum(data['铁次时间'] == value)  # 铁次时间中等于系统和现场评分表时间value的个数
            scoreDict['铁次'].extend(data.index[data['铁次时间'] == value])
            scoreDict['系统评分'].extend([score.loc[value]['系统评分']] * count)
            scoreDict['现场评分'].extend([score.loc[value]['现场评分']] * count)
        scoreDf = pd.DataFrame(scoreDict).set_index('铁次').sort_index()
        data = pd.merge(data, scoreDf, how='left', left_index=True, right_index=True)
        return data

    def addScoreLabel(self, data, scoreRange):
        '''
        对系统评分和现场评分按照分数范围(scoreRange)进行标定, 例如大于80小于90的分数标定为0

        Parameters
        ----------
            data: 待添加标签的数据 类型: dataframe, index为铁次号, 列数据包含有系统评分和现场评分
            scoreRange: 每一类所对应的分数取值范围 类型: list，最大的数在列表[0]位置
        Return
        ------
            类型: dataframe, 在data中添加了系统评分和现场评分的标签
        '''
        systemLabelDict = {'系统铁次号': [], '系统label': []}
        sceneLabelDict = {'现场铁次号': [], '现场label': []}
        label = 0
        for i in range(len(scoreRange) - 1):
            sysCondition = (data['系统评分'] < scoreRange[i]) & (data['系统评分'] >= scoreRange[i + 1])  # 为了提取该分数区间段内的数据
            sceneCondition = (data['现场评分'] < scoreRange[i]) & (data['现场评分'] >= scoreRange[i + 1])
            systemLabelDict['系统铁次号'].extend(data.index[sysCondition])
            systemLabelDict['系统label'].extend(sum((sysCondition)) * [label])

            sceneLabelDict['现场铁次号'].extend(data.index[sceneCondition])
            sceneLabelDict['现场label'].extend(sum(sceneCondition) * [label])
            label += 1
        ironAndLabel1 = pd.DataFrame(systemLabelDict).set_index('系统铁次号').sort_index()
        ironAndLabel2 = pd.DataFrame(sceneLabelDict).set_index('现场铁次号').sort_index()
        ironAndLabel = pd.merge(ironAndLabel1, ironAndLabel2, how='outer', left_index=True, right_index=True)
        res = pd.merge(data, ironAndLabel, how='left', left_index=True, right_index=True)
        return res

    def saveData(self, save=False, savePath=None):
        '''
        保存数据

        Parameters
        ----------
            save: 是否保存数据 类型: boolean
            savePath: 保存地址 类型: str
        '''
        if save == True:
            self.ironData.to_excel(savePath)

    def dealStart(self, ):
        if self.interp == True:
            self.ironData = self.interpolate(self.ironData)  # 前向插值和后向插值
        if self.tangJueLabel is not None:
            # 添加唐珏老师的标签列
            self.ironData = pd.merge(self.ironData, self.tangJueLabel, how='left', left_index=True, right_index=True)
            # 添加受铁开始时间和结束时间
        self.ironData = pd.merge(self.ironData, self.ironTime, how='left', left_index=True, right_index=True)
        self.ironData = self.addIronTime(self.ironData,
                                         self.ironData['受铁结束时间'])  # 为data添加一列铁次时间(格式: 年月日)数据, 用以添加评分数据, 最后会删除
        self.ironData = self.scoreCalibration(self.ironData, self.scoreData)  # 为铁次数据添加评分
        self.ironData = self.ironData.drop('铁次时间', axis=1)  # 丢弃为添加评分创建的铁次时间列
        if self.scoreRange is not None:
            self.ironData = self.addScoreLabel(self.ironData, self.scoreRange)
        self.saveData(self.save, self.savePath)


if __name__ == "__main__":
    ironTimePath = './铁次时间.xlsx'  # 铁次时间的整合表  # 来了新数据需要添加
    scorePath = './分数.xlsx'  # 系统评分和现场评分的整合表
    tangJueLabelPath = './铁次结果汇总_5h滞后v3.0 (1).xlsx'  # 带有唐珏老师标签的数据
    dataPath = './铁次5h滞后_v3.5.xlsx'  # 数据
    savePath = '增加分数.xlsx'  # 数据保存的地址
    # scoreRange = [100, 85, 80, 75, 0]# 四分类
    scoreRange = [100, 85, 75, 0]  # 三分类

    ironTime = pd.read_excel(ironTimePath).set_index('铁次号')
    score = pd.read_excel(scorePath).set_index('日期')
    ironData = pd.read_excel(dataPath).set_index('铁次号')
    tangJueLabel = pd.read_excel(tangJueLabelPath).set_index('铁次号')

    process = DataProcess(ironData, ironTime=ironTime, scoreData=score, scoreRange=None, tangJueLabel=tangJueLabel,
                          save=True, savePath=savePath)
    process.dealStart()
