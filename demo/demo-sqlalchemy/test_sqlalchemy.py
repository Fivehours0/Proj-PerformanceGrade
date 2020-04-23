from sqlalchemy import create_engine
import pandas as pd
import numpy as np
"""
sqlalchemy 适用于所有sql
psycopy2 适用于 postgreSQL

"""
# 教程参考
# https://blog.csdn.net/chang1976272446/article/details/71424961
if __name__ == '__main__':

    #create_engine说明：dialect[+driver]://user:password@host/dbname[?key=value..]
    engine = create_engine('postgresql://postgres：a2102135@localhost:5432/runoobdb')
