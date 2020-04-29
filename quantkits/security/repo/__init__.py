# -*- coding: utf-8 -*-
# @Time    : 29/4/2020 11:41 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: __init__.py.py
# @Software: PyCharm
from datetime import datetime
from quantkits.security import Security


class Repo(Security):

    """
    repos and reverse repos are two sides of the same coin—or rather, transaction—reflecting the role of each party.
    A repo is an agreement between parties where the buyer agrees to temporarily purchase a basket or group of
    securities for a specified period. The buyer agrees to sell those same assets back to the original owner at a
    slightly higher price using a reverse repo agreement.

    The buyer acts as a short-term lender, while the seller acts as a short-term borrower.

    The securities being sold are the collateral.
    """

    def __init__(self, collateral:Security, number_of_securities:int, maturity_date:datetime, enter_date:datetime,
                 repo_rate:float):
        self.collateral = collateral
        self.number_of_securities = number_of_securities
        self.maturity_date = maturity_date
        self.enter_date = enter_date
        self.repo_rate = repo_rate

    def __str__(self):
        return f"Repo[{self.__dict__}]"

    __repr__=__str__