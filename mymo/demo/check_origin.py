# -*- coding: utf-8 -*-
from mymo.get_things import *

if __name__ == '__main__':
    """
    画探尺波动图
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
    # 总时间段图
    rule.plot()
    plt.show()

    # bigger_than_10 = rule[rule['采集项值'] > 3]
    # tp = bigger_than_10.index[4]
    '''
    2019-10-26 08:44:38  1.989   0.0
    2019-10-28 08:23:54  1.633   0.0
    2019-11-11 15:47:37  1.883   0.0
    2019-11-11 15:48:37  1.883   0.0
    2019-11-16 03:39:48  1.924   0.0
    2019-11-19 15:09:41  2.053   0.0
    2019-11-19 15:10:41  2.053   0.0
    2019-11-21 11:22:44  1.825   0.0
    2019-11-23 03:03:42  1.834   0.0
    2019-11-23 14:40:42  1.770   0.0
    2019-11-24 03:48:42  2.192   0.0
    2019-11-26 06:26:31  1.987   0.0
    2019-11-30 15:42:35  1.774   0.0
    '''

    # 小时间段图
    tp = pd.to_datetime('2019-11-23 03:03:42')
    part = rule.loc[str(tp - pd.Timedelta('30min')): str(tp + pd.Timedelta('30min')), '采集项值']
    part.plot()
    plt.scatter(part.index, part.values, c='r')
    plt.show()
