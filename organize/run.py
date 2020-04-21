"""
一次性生成
整理好的铁次、天数据
"""
from organize.iron import main as imain


# from organize.day import main as dmain


def main(t_id):
    # t_id = 201  # 数据的ID号

    print("开始把数据id号为{}的数据整理成铁次数据,且带有5小时的滞后处理".format(t_id))
    imain(table_id=t_id, five_lag=True)

    print("开始把数据id号为{}的数据整理成铁次数据,且不带有滞后处理".format(t_id))
    imain(table_id=t_id, five_lag=False)

    # print("开始把数据id号为{}的数据整理成每日型数据".format(t_id))
    # dmain(table_id=t_id)

    # print("开始对100指标抽取出21,41版本, 并且进行缺失填充")
    # path = "organize/cache/"
    # files = ["铁次无滞后.xlsx",
    #          "铁次5h滞后.xlsx",
    #          "每日.xlsx"]

    # emain(path, files[0], data_type='iron')
    # emain(path, files[1], 'iron')
    # emain(path, files[2], 'day')

    return None


def chdir():
    # 切换工作路径
    import os
    path = "../"
    os.chdir(path)
    a = os.getcwd()
    print(a)


if __name__ == '__main__':

    chdir()





