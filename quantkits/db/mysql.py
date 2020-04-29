# -*- coding: utf-8 -*-
# @Time    : 2/8/2019 4:40 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: mysql.py
# @Software: PyCharm

from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

from config.config import MYSQL_CONFIG

Base = declarative_base()

class DB:
    """MySQL/MariDB"""

    def create_engine(self, user:str, password:str, address:str, port:int, database:str):
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{address}:{port}/{database}?charset=utf8mb4&autocommit=true")
        self.engine = engine
        # 绑定引擎
        self.metadata = MetaData(engine)

    @property
    def conn(self):
        self._conn = self.engine.connect()
        return self._conn

    def close_conn(self):
        self._conn.close()

    def create_table(self):
        # 创建数据表，如果数据表存在则忽视
        self.metadata.create_all()



if __name__=="__main__":
    # db = DB()
    # db.create_engine(user="user",
    #                  password="pwd",
    #                  address="localhost",
    #                  port=3306,
    #                  database="mydb")
    # results_table = Table('results', db.metadata, autoload=True)
    # res = results_table.select(results_table.c.Date==date(2019,6,23)).execute()
    # # res = results_table.select(results_table.c.Date >= "2019-06-23").execute()
    #
    # for item in res.fetchall():
    #     print(item)

    db = DB()
    db.create_engine(**MYSQL_CONFIG.get("horse"))

    # 定义表格
    fixtures_table = Table('fixtures', db.metadata,
                       Column('index', Integer, primary_key=True),
                       Column('Date', Date),
                       Column('Location', String(2))
                       )

    db.create_table()





