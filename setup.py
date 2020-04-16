"""
项目代码的入口
"""
# from preprocess import *
# from mymo.get_things import *
from mymo.dailyData.daily_preprocess_v3_alpha import *

if __name__ == '__main__':

    # 铁次处理的远端部署代码
    # main(five_lag=True)

    # 每日处理的测试
    res = main()

    # # 测试模块
    # params = ['炉缸温度1', '炉缸温度2', '炉缸温度3', '炉缸温度4', '炉缸温度5', '炉缸温度6',
    #           '炉底温度1', '炉底温度2', '炉底温度3', '炉底温度4', '炉底温度5', '炉底温度6', '炉缸中心温度']
    #
    # for i in params:
    #     print(i, " in ", find_table(i, 201))

    # self = Solution(201)
    # param_list = "40赤块_CaO 40赤块_CaO 冶金焦综合样_CaO 冶金焦综合样_CaO".split()
    # df = self.get_df(param_list[0])
    # res = self.process_chemical(param_list, df)
    # self.get_slag_amount()
    # self.get_shaojie()
    # res =self.res

    print("Work done !")
