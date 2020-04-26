# -*- coding: UTF-8 -*-
import os
from organize.iron import *

if __name__ == '__main__':
    os.chdir('../')
    print(os.getcwd())

    sol = Solution(20)
    sol.get_chemical()

