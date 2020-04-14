"""
使用 momy 的入口

"""
from mymo.dailyData.daily_preprocess_v3_alpha import *
from mymo.get_things import *
if __name__ == '__main__':

    # # 测试模块
    # solv = Solution(201)
    # self = solv
    # solv.get_loading()
    # solv.get_wind()
    # res = self.res


    #
    # find_table('炉腹煤气发生量', 201)
    # df = get_df('炉腹煤气发生量',201)
    # set(df['采集项名称'])

    # main()

    solv = Solution(20)
    solv.get_deltaR2()
    solv.get_deltaTi()
    dfs = solv.res
    dfs.to_excel('每日数据20.xlsx')  # 暂时保存一下