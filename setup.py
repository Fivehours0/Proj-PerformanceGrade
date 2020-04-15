"""
项目代码的入口
"""
from preprocess import *
# from mymo.get_things import *

if __name__ == '__main__':

    # 远端部署代码
    main(five_lag=True)

    # # 测试模块
    # self = Solution(201)
    # param_list = "40赤块_CaO 40赤块_CaO 冶金焦综合样_CaO 冶金焦综合样_CaO".split()
    # df = self.get_df(param_list[0])
    # res = self.process_chemical(param_list, df)
    # self.get_slag_amount()
    # self.get_shaojie()
    # res =self.res

    print("Work done !")



