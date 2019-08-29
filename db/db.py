# -*- coding: utf-8 -*-
# @Time    : 2/8/2019 4:40 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: db.py
# @Software: PyCharm

from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import MetaData
from datetime import date

class DB:

    def create_engine(self, user:str, password:str, address:str, port:int, database:str):
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{address}:{port}/{database}")
        conn = engine.connect()
        self.engine = engine
        self.metadata = MetaData(engine)
        self.conn = conn


if __name__=="__main__":
    db = DB()
    db.create_engine(user="user",
                     password="pwd",
                     address="localhost",
                     port=3306,
                     database="mydb")
    results_table = Table('results', db.metadata, autoload=True)
    res = results_table.select(results_table.c.Date==date(2019,6,23)).execute()
    # res = results_table.select(results_table.c.Date >= "2019-06-23").execute()

    for item in res.fetchall():
        print(item)




