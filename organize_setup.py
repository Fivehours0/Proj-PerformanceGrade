"""
orgaize模块的程序入口
"""
from organize.run import main

if __name__ == '__main__':
    """
    新数据来的时候要进行的步骤
    1. 做榨菜 参考 organize.make_pickle.py
    2. 设置 organize.config.config.py 文件
    3. 设置本程序的 table_id 值
    
    """
    table_id = 201
    main(table_id)

    """
    在目录
    organize/cache/
    下
    会生成三个文件
    """

    print("done!")
