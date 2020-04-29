# -*- coding: utf-8 -*-
# @Time    : 29/4/2020 11:39 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: __init__.py.py
# @Software: PyCharm
from quantkits.security import Security


class Equity(Security):
    """Equity"""

    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return f"Equity[symbol={self.symbol}]"

    __repr__=__str__