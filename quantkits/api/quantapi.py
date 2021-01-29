# -*- coding: utf-8 -*-
# @Time    : 27/1/2021 12:06 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: quantapi.py
# @Software: PyCharm

import json
import requests

class Financials:
    """
    API to retrieve HK companies' financial data
    """

    def __init__(self, stock_code:str, host:str="47.91.158.196", port:int=8000):
        self.HOST = host
        self.PORT = port
        self.query_code(stock_code)

    def get_balance_sheets(self):
        self._validate_code(self._data.get("code"), self.stock_code)
        return self._data.get("data").get("assets")

    def get_income_statements(self):
        self._validate_code(self._data.get("code"), self.stock_code)
        return self._data.get("data").get("profit")

    def get_cash_flows(self):
        self._validate_code(self._data.get("code"), self.stock_code)
        return self._data.get("data").get("cash")

    def query_code(self, stock_code:str):
        self.stock_code = stock_code
        self._data = self.fetch_data()

    def fetch_data(self):
        with requests.Session() as s:
            resp = s.get(f"http://{self.HOST}:{self.PORT}/financials/?code={self.stock_code}")
            data = json.loads(resp.text)
        return data

    def post_data(self, data:json):
        with requests.Session() as s:
            resp = s.post(f"http://{self.HOST}:{self.PORT}/financials/", json=data)
        return resp

    def _validate_code(self, ret_code, query_code):
        assert ret_code == query_code, f"Error: return stock {ret_code} does not match query stock {query_code}"


if __name__=="__main__":
    stock_codes = ["00002", "00003"]
    for stock_code in stock_codes:
        # 建立API接口
        api = Financials(stock_code)

        # 讀取數據
        balance_sheets = api.get_balance_sheets()
        income_statements = api.get_income_statements()
        cash_flows = api.get_cash_flows()
        print(f"balance sheets: {balance_sheets.keys()}")
        print(f"income statements: {income_statements.keys()}")
        print(f"cash flows: {cash_flows.keys()}")

        # 寫入數據
        data_path = f"/Users/joseph/Dropbox/code/futu_scrape/financials/{stock_code}.json"
        with open(data_path) as f:
            data = json.load(f)
            json_data = json.dumps({"code": stock_code, "data": data})
        api.post_data(data=json_data)

