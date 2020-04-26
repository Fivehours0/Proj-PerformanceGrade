import pandas as pd

if __name__ == '__main__':
    df2 = pd.read_excel('data/二批数据100指标整理v1.0.xlsx', index_col=0)
    # df3 = pd.read_excel('data/三批数据100指标整理v1.0.xlsx', index_col=0)

    # 系统评分
    df_score1 = pd.read_excel('data/高炉稳定性评价分数_西昌_20200411(1).xlsx')
    df_score1.set_index('评价帧', inplace=True)
    # s1 = df_score1['评价得分']
    # 现场评分
    df_score2 = pd.read_excel('data/高炉稳定性评价分数_西昌_20200411(1).xlsx', sheet_name='现场评分结果', index_col=0)

    scores = pd.DataFrame()
    scores['系统评分'] = df_score1['评价得分']
    scores['现场评分'] = df_score2['评分']

    # df = pd.concat([df2, df3])
    merged = pd.merge(df2, scores, how='inner', left_index=True, right_index=True)
    merged.to_excel('每日训练数据集100版本.xlsx')

