# -*- coding: UTF-8 -*-
"""
预处理程序入口

复制到项目工作路径，然后工作
"""

from organize2.iron import interface as iron_main
from organize2.concat_and_fill import concat_and_fill

if __name__ == '__main__':
    print("正在处理第一批数据")
    iron_main(19)
    print("正在处理第二批数据")
    iron_main(20)
    print("正在处理第三批数据")
    iron_main(201)
    concat_and_fill()
