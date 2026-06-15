# -*- coding: utf-8 -*-

import sqlite3
import time


class BaseEngine:

    def __init__(self):

        self.db_path = "data/etf.db"

    def extract(self):
        pass

    def transform(self):
        pass

    def load(self):
        pass

    def run(self):

        start = time.time()

        self.extract()
        self.transform()
        self.load()

        cost = round(time.time() - start, 2)

        print(f"[OK] 完成：{self.__class__.__name__}")
        print(f"耗时：{cost} 秒")
