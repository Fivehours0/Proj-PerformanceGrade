import pandas as pd
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine


def connect_db():
    """
    链接数据库
    教程来自：https://www.jianshu.com/p/34afe4072598
    :return:
    """
    try:
        conn = psycopg2.connect(database='postgres', user='postgres',
                                password='xuhang', host='127.0.0.1', port=5432)
    except Exception as e:
        error_logger.error(e)
    else:
        return conn
    return None


def close_db_connection(conn):
    """
    关闭数据库
    教程来自：https://www.jianshu.com/p/34afe4072598
    :param conn:
    :return:
    """
    conn.commit()
    conn.close()


def create_db():
    """
    创建数据库
    教程链接同上
    :return:
    """
    conn = connect_db()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute(
        " CREATE TABLE IF NOT EXISTS dictionary("
        "english VARCHAR(30), "
        "chinese VARCHAR(80), "
        "times SMALLINT, "
        "in_new_words SMALLINT)"
    )
    close_db_connection(conn)


if __name__ == '__main__':
    # 链接数据库
    conn = psycopg2.connect(database='runoobdb', user='postgres',
                            password='a2102135', host='127.0.0.1', port=5432)

    # # 读取数据
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM test2")
    # rows = cur.fetchall()

    # 直接读入dataFrame  https://www.cnblogs.com/yyjjtt/p/11255044.html
    sql_getall = 'select * from test2'
    rows = pd.read_sql(sql=sql_getall, con=conn)

    # 批量插入
    data_test = pd.DataFrame(data=[[1, '武则天'], [3, '李世民']], columns=['PID', 'name'])
    # data_test.append([[1, '秦始皇']])
    data_test = data_test.append({'PID': 2, 'name': '秦始皇'}, ignore_index=True)
    # create_engine说明：dialect[+driver]://user:password@host/dbname[?key=value..]
    engine = create_engine('postgresql://postgres:a2102135@localhost:5432/runoobdb')
    try:
        data_test.to_sql(name='test3', schema='public', con=engine, if_exists='append', index=False)
    except psycopg2.IntegrityError:
        print("因为主键限制不可重复插入")
    except sqlalchemy.exc.IntegrityError:
        print("因为主键限制不可重复插入")
    # # 插入
    # cur.execute("INSERT INTO test2 "
    #             "VALUES(2,'秦始皇')")
    # conn.commit()
