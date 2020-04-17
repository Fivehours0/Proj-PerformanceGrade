import pandas as pd
import numpy as np


# SQL 字段

FILE = '../这会是个数据库吗.xlsx'
if __name__ == '__main__':
    data = np.random.rand(5, 2)

    df = pd.DataFrame(data, columns=['A', 'B'])
    df.to_excel(FILE)

    rdf = pd.read_excel(FILE, index_col=0)

    df = pd.DataFrame(np.random.rand(1, 2), columns=['A', 'B'], index=[5])
    df.to_excel(FILE)