"""
把之前的铁次数据给摘出来，指标以 钢研院每日指标为基准
"""
import pandas as pd


# if __name__ == '__main__':
# 没有滞后的
# root_path = "C:/Users/Administrator/Documents/GitHub/BF-grading-range/"
def generate_gyy_table(file, output_file):
    """
    生成钢铁研究院版本的结果
    :param output_file: 输出文件路径&名
    :param file: 'data/铁次结果汇总_无滞后处理v2.0.xlsx'
    :return:
    """

    # file_add = 'data/钢研院指标的铁次化数据抽取/每小时高炉利用系数(出铁速率版).xlsx'

    df = pd.read_excel(file, index_col=0)
    # df_addition = pd.read_excel(file_add, index_col=0)

    # df = pd.merge(df_addition, df_first, how='outer', left_index=True, right_index=True)

    contrast = pd.read_excel("data/钢研院指标的铁次化数据抽取/钢研院参数对照表.xlsx")  # 读入对照表
    list_need = contrast['我们的铁次参数']
    list_need = list_need.dropna().to_list()

    df_third = df[list_need]
    df_third.to_excel(output_file)


def generate_all_gyy_table():
    """
    生成 19 20 的数据，后期可能有拓展。。
    :return:
    """

    input_file = 'data/铁次结果汇总_无滞后处理v2.1.xlsx'
    output_file = "data/钢研院指标的铁次化数据抽取/release/铁次结果汇总_无滞后v3.0.xlsx"
    generate_gyy_table(input_file, output_file)

    input_file = 'data/铁次结果汇总_5h滞后处理v2.1.xlsx'
    output_file = "data/钢研院指标的铁次化数据抽取/release/铁次结果汇总_5h滞后v3.0.xlsx"
    generate_gyy_table(input_file, output_file)
