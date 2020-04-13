
'''
计算以下指标日均(2019-10-01 ~ 2019-11-30)数值
燃料比,kg/t
煤比,kg/t
[C],%
[Ti],%
[Si],%
[S],%
δ[Ti]
R2
R3
TiO2,%
MgO/Al2O3
δR2
M40,%
M10,%
CRI,%
CSR,%
S,%
'''

import numpy as np
import pandas as pd

DICT = {
    '焦炭粒度、冷强度_M40': '上料质量表',
    '焦炭粒度、冷强度_M10': '上料质量表',
    '焦炭热性能_CRI': '上料质量表',
    '焦炭热性能_CSR': '上料质量表',
    '焦炭工分_St': '上料质量表'
}
df_slag = pd.read_pickle('./pkl/' + '炉渣成分表' + '.pkl')
df_slag = df_slag[df_slag['铁次号'] >= '20000000']  # 提取出#2高炉的数据
df_slag = df_slag[df_slag['铁次号'] < '30000000']

df_feed = pd.read_pickle('./pkl/' + '上料质量表' + '.pkl')

df_iron_comp = pd.read_pickle('./pkl/' + '铁水成分表' + '.pkl')
df_iron_comp = df_iron_comp[df_iron_comp['铁次号'] >= '20000000']  # 提取出#2高炉的数据
df_iron_comp = df_iron_comp[df_iron_comp['铁次号'] < '30000000']


def get_coke():
    """
    计算焦炭5个性能参数日均值

    数据源A 本身就归好了日期, 进行groupby操作即可
    """
    res = pd.DataFrame(data=None,
                       index=pd.date_range(start='2019-10-01', end='2019-11-30')
                       )

    param_list = [
        '焦炭粒度、冷强度_M40',
        '焦炭粒度、冷强度_M10',
        '焦炭工分_St',
        '焦炭热性能_CRI',
        '焦炭热性能_CSR']

    df = df_feed
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
    df['采集项值'] = pd.to_numeric(df['采集项值'])
    for param in param_list:
        # param = '焦炭粒度、冷强度_M40'
        temp = df.groupby('采集项名称').get_group(param)
        temp1 = temp.groupby('业务处理时间').mean()
        res[param] = temp1['采集项值'].copy()
    # 导出结果
    # res.to_excel('焦炭5.xlsx')
    return res


def get_molten_iron():
    param_list = [
        '[C]',
        '[Ti]',
        '[Si]',
        '[S]']
    res = pd.DataFrame(data=None,
                       index=pd.date_range(start='2019-10-01', end='2019-11-30'))
    df = df_iron_comp
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
    df['采集项值'] = pd.to_numeric(df['采集项值'])
    for param in param_list:
        # param = '[C]'
        temp = df.groupby('采集项名称').get_group(param)
        temp1 = temp.groupby('业务处理时间').mean()
        res[param] = temp1['采集项值'].copy()
    # 导出结果
    # res.to_excel('焦炭5.xlsx')
    return res


def get_deltaTi():
    res = pd.DataFrame(data=None,
                       index=pd.date_range(start='2019-10-01', end='2019-11-30'))
    df = df_iron_comp
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
    df['采集项值'] = pd.to_numeric(df['采集项值'])
    param = '[Ti]'
    temp = df.groupby('采集项名称').get_group(param)
    temp = temp.loc[:, ['业务处理时间', '采集项值']]
    temp1 = temp.groupby('业务处理时间').apply(np.max) \
            - temp.groupby('业务处理时间').apply(np.min)
    res['delta_Ti'] = temp1['采集项值'].copy()
    # 导出结果
    # res.to_excel('焦炭5.xlsx')
    return res


def get_slag():
    res = pd.DataFrame(data=None,
                       index=pd.date_range(start='2019-10-01', end='2019-11-30'))
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
        # param = '[C]'
        temp = df.groupby('采集项名称').get_group(param)
        temp1 = temp.groupby('业务处理时间').mean()
        res[param] = temp1['采集项值'].copy()

    res['R2'] = res['(CaO)'] / res['(SiO2)']
    res['R3'] = (res['(CaO)'] + res['(MgO)']) / res['(SiO2)']
    res['镁铝比'] = res['(MgO)'] / res['(Al2O3)']
    return res


def get_delta_R2():
    # 计算delta_R2
    res = pd.DataFrame(data=None,
                       index=pd.date_range(start='2019-10-01', end='2019-11-30'))

    df = df_slag
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])  # 格式化
    df['采集项值'] = pd.to_numeric(df['采集项值'])  # 格式化

    CaO = df.groupby('采集项名称').get_group('(CaO)')  # 筛选
    CaO = CaO.groupby('铁次号').mean()

    SiO2 = df.groupby('采集项名称').get_group('(SiO2)')  # 筛选
    SiO2 = SiO2.groupby('铁次号').mean()
    R2 = CaO / SiO2

    # 处理过程中 业务处理日期丢了 此段代码负责找补回来
    tvo = df.loc[:, ['业务处理时间', '铁次号']]
    tvo2 = tvo.drop_duplicates()
    tvo2 = tvo2.set_index('铁次号')
    nR2 = pd.merge(R2, tvo2, right_index=True, left_index=True)

    res['delta_R2'] = nR2.groupby('业务处理时间').apply(np.max)['采集项值'] \
                      - nR2.groupby('业务处理时间').apply(np.min)['采集项值']

    return res


def get_ratio():
    res = pd.DataFrame()

    ## 日产量
    df = pd.read_pickle('./pkl/铁水实绩表.pkl')
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])
    df['采集项值'] = pd.to_numeric(df['采集项值'])
    res['日产量'] = df.groupby('业务处理时间').sum()['采集项值']

    ### 焦比
    df = pd.read_pickle('./pkl/上料实绩表.pkl')
    df['采集项值'] = pd.to_numeric(df['采集项值'])
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间']).dt.floor('d')
    df1 = df.groupby('采集项名称').get_group('冶金焦（自产）')
    df2 = df.groupby('采集项名称').get_group('小块焦')

    res['焦量'] = df1.groupby('业务处理时间').sum()['采集项值'] \
                + df2.groupby('业务处理时间').sum()['采集项值']
    res['焦比'] = res['焦量'] / res['日产量'] * 1000

    # #  煤比
    df = pd.read_pickle('./pkl/西昌2#高炉采集数据表_喷吹系统.pkl')
    df = df.groupby('采集项名称').get_group('日喷煤量')
    df['采集项值'] = pd.to_numeric(df['采集项值'])
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间']).dt.floor('d')
    temp = df.groupby('业务处理时间').apply(np.max)
    res['日喷煤量'] = temp.shift(-1).loc[:'2019-11-05', '采集项值']
    res['煤比'] = res['日喷煤量'] / res['日产量'] * 1000

    res['燃料比'] = res['焦比'] + res['煤比']
    return res


if __name__ == '__main__':
    res1 = get_coke()
    # res2 = get_molten_iron()
    # res3 = get_deltaTi()
    # res4 = get_slag()
    # res5 = get_delta_R2()
    # res6 = get_ratio()