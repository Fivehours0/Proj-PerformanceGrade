# -*- coding: UTF-8 -*-
"""
实验 python 的局部变量
"""


class TestLocalVar:
    GLOBAL_VARIABLE = 0

    def sub_fun1(self):
        print(TestLocalVar.GLOBAL_VARIABLE)

    def fun1(self):
        self.sub_fun1()



