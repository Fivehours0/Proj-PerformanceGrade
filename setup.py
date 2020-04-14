"""
使用 momy 的入口

"""
from mymo.dailyData.daily_preprocess_v3_alpha import *
from mymo.get_things import *
if __name__ == '__main__':

    # # 测试模块
    solv = Solution(201)
    self = solv
    # solv.get_gas()
    # res = self.res





    # 查询表中都有什么指标 好一网打尽
    find_table('[铁水温度]', 201)
    df = get_df('[铁水温度]',201)
    set(df['采集项名称'])

    # 调用main()
    # main()

    # 第二批处理的 ΔR2 Ti 错了
    # solv = Solution(20)
    # solv.get_deltaR2()
    # solv.get_deltaTi()
    # dfs = solv.res
    # dfs.to_excel('每日数据20.xlsx')  # 暂时保存一下