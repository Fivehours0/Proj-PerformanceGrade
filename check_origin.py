# -*- coding: utf-8 -*-
from mymo.get_things import *

if __name__ == '__main__':
    """
    直接找 同一采集时刻下的 探尺探测段的数据有点少。
    """
    time_table = get_time_table(19)

    df = get_df('探尺（东）', 19)
    df['采集项值'] = pd.to_numeric(df['采集项值'])
    df['业务处理时间'] = pd.to_datetime(df['业务处理时间'])

    rules_name = ['探尺（南）', '探尺（东）', '探尺（西）']

    rule_name = rules_name[0]
    rule = df.groupby('采集项名称').get_group(rule_name).set_index('业务处理时间')  # 筛选
    # 画全部的探尺波动图：
    rule[rule['采集项值'] > 10] = np.nan
    rule.plot()
    plt.show()

    # part = rule.loc['2019-10-01 16:25:00':'2019-10-01 16:35:00', '采集项值'] # 为何 只用一秒就从 10 跳的2？
    # part.plot()
    # plt.scatter(part.index, part.values, c='r')
    # plt.show()

    # 找 >10的点
    bigger_than_10 = rule[rule['采集项值'] > 3]
    tp = bigger_than_10.index[4]
    part = rule.loc[str(tp - pd.Timedelta('6h')): str(tp + pd.Timedelta('-4h')), '采集项值']
    part.plot()
    plt.scatter(part.index, part.values, c='r')
    plt.show()

    # for hooker_name in brothel:
    #     hooker = df.groupby('采集项名称').get_group(hooker_name).set_index('业务处理时间')  # 筛选
    #
    #     hooker.drop(columns=['采集项编码', '采集项名称'], inplace=True)
    #     hooker.rename(columns={'采集项值': hooker_name}, inplace=True)
    #     hooker[hooker_name][hooker[hooker_name] > 1e7] = None  # 去除1e7 的异常值
    #     hooker['delta_time'] = np.nan
    #     hooker['delta_time'].iloc[1:] =  hooker.index[1:] - hooker.index[:-1]
    #
    #     hooker[hooker_name][hooker[hooker_name] < 0] = np.nan
    #     hooker.dropna(inplace=True)
    #
    #     hooker['delta_time'][hooker['delta_time'] < pd.Timedelta('60s')] = np.nan
    #     hooker.dropna(inplace=True)
    #
    #     hookers.append(hooker)

    #  # 找出 所有 在同一时刻 三个探尺高度数据都不缺失的样本
    # temp = pd.merge(hookers[0], hookers[1], how="inner", left_index=True, right_index=True)
    # blondie = pd.merge(temp, hookers[2], how="inner", left_index=True, right_index=True)
    #
    #     # 计算极差
    # wife = pd.DataFrame()
    # wife['采集项值'] = blondie.max(axis=1) - blondie.min(axis=1)
    # res = pd.DataFrame()
    # res['探尺差'] = time_table.iloc[3:].apply(lambda x: wife.loc[x['受铁开始时间']:x['受铁结束时间'], '采集项值'].mean(),
    #                                             axis=1)
    #
    # draw = grouped.loc['2019-10-15 12:00:00':'2019-10-15 12:30:00','采集项值']
    # draw.plot()
    # plt.scatter(draw.index,draw.values,c='r')
