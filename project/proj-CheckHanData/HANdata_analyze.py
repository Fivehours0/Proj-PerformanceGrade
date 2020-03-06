import pandas as pd
import numpy as np

df_h = pd.read_excel('按分钟对齐数据版.xlsx')
df_h = df_h.set_axis(labels=df_h.iloc[0,:],axis = 1)
df_h.drop(index = 0, inplace=True)
df_h_desc = df_h.iloc[:,1:].astype(np.float64).describe()

df_me = pd.read_excel('西昌#2高炉每日整理数据.xlsx', sheet_name = 2)
df_me.drop(index=[0,1], inplace=True)
df_me_desc = df_me.loc[:,'日产量,t/d':'碱负荷,kg/t'].astype(np.float64).describe()


# 透气性指数差别大, 韩老师的透气性指数中位数为 2169 18年的数据 2536
# 我们的是2457
# std = 100

print(df_h_desc['透气性指数'])
'''
                    透气性指数中位数    变化幅度(max-min)/2
韩老师团队(/分钟):          2169            404
我们(/天):                 2457            107
18年数据(/天):             2538            137
'''
