import pandas as pd

data1 = [[1, 3],
         [5, 6]]
columns1 = ['A', 'B']
df1 = pd.DataFrame(data1, columns=columns1, index=[0, 3])

data2 = [[2, 3],
         [3, 5]]

columns2 = ['C', 'D']

df2 = pd.DataFrame(data2, columns=columns2, index=[0, 1])
# df1[df2.columns] = df2
df3 = pd.concat([df1, df2],axis=1)