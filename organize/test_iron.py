# -*- coding: UTF-8 -*-
"""
iron的测试文件
"""
import pandas as pd
from organize.iron import Solution
from organize.iron import ORGANIZE_CONFIG_XLSX
from organize.iron import CHEMICAL_TABLE_NAME
import os

if __name__ == '__main__':
    os.chdir('../')
    print("工作路径")
    print(os.getcwd())

    param_table = pd.read_excel(ORGANIZE_CONFIG_XLSX)
    param_list_chemical = list(param_table[CHEMICAL_TABLE_NAME].dropna())

    group_can = []
    group_cannt = []
    for i in param_list_chemical:
        if len(i) >= 9 and i[:9] == '高炉沟下烧结矿粒度':
            group_cannt.append(i)
        else:
            group_can.append(i)


    # sol = Solution(20)
    # sol.get_ratio()
    # sol.get_slag()
    # sol.get_slag_amount()
    #
    # sol.get_chemical()
