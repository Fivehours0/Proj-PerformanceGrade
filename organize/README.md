# organize模块介绍

## 说明
本模块进行"每日,铁次"数据整理,
每日数据暂时不整理(后期可能会整理班次)

## 步骤
新数据来的时候要进行的步骤
1. 做榨菜 参考 `organize.make_pickle.py`
2. 设置 `organize.config.config.py` 文件
3. 设置本程序的 `table_id` 值

在目录`organize/cache/`下会生成N多文件

## 数据整理的版号规范

    版号规范 A.B.C
    
    A： 因企业的发来的数据批次而变
    
    B： 老师的需求变动而变
    
    C： 我们的小修改



