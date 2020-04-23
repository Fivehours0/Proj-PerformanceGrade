"""
演示一下excel 文件导入的 PostgreSQL 中
以及读取
"""
import pandas as pd
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine

df = pd.read_excel('铁次100plus_v3.4.xlsx')  # load data

# 抽取采集值
extract_col_index = [0] + list(range(3, 112))
df_value = df.iloc[:, extract_col_index]

# melt
df_melted = pd.melt(df_value, id_vars=['铁次号'], var_name='采集项名称', value_name='采集项值')
df_melted.drop_duplicates(inplace=True)

engine = create_engine('postgresql://postgres:a2102135@localhost:5432/runoobdb')  # 链接数据库
df_melted.to_sql(name='iron_data', schema='public', con=engine, if_exists='append', index=False)

# 读取
sql_getall = 'select * from iron_data'
conn = psycopg2.connect(database='runoobdb', user='postgres',
                        password='a2102135', host='127.0.0.1', port=5432)  # 链接数据库
rows = pd.read_sql(sql=sql_getall, con=conn)
df_pivoted = pd.pivot(rows.iloc[:, 1:], index='铁次号', columns='采集项名称', values='采集项值')

# 后面应当对 df_pivoted 进行缺失填充
