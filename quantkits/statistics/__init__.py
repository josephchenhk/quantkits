# -*- coding: utf-8 -*-
# @Time    : 29/4/2020 11:13 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: __init__.py.py
# @Software: PyCharm

import pandas as pd
import numpy as np

def calculate_financials(data:pd.DataFrame, rf:float=0.005)->pd.DataFrame:
    '''Return, annualized return, volatility, annualized volatility, risk-adjusted return, maximum drawdown'''
    invest_period = (data.index[-1] - data.index[0]).days
    invest_period_srs = pd.Series(dict(zip(data.columns, [invest_period for _ in data.columns])))
    start_srs = pd.Series(dict(zip(data.columns, [data.index[0].strftime("%Y-%m-%d") for _ in data.columns])))
    end_srs = pd.Series(dict(zip(data.columns, [data.index[-1].strftime("%Y-%m-%d") for _ in data.columns])))
    R = (data.iloc[-1] - data.iloc[0]) / data.iloc[0]
    AR = (1 + R) ** (365.25 / invest_period) - 1
    data1 = data.pct_change()
    data1.drop(data1.index[0], inplace=True)
    Vol = data1.std()
    AVol = np.sqrt(252) * Vol
    AdjR = AR / AVol
    MDD, MDD_dates = max_drawdown(data)

    '''
    香港時間1/11/2018
    早上11時15分的結算率。
    到期日	港元利息結算率

    隔夜	0.50000
    '''
    SR = (AR - rf) / AVol
    df = pd.concat([invest_period_srs, start_srs, end_srs, R, AR, Vol, AVol, AdjR, MDD, MDD_dates, SR], axis=1)
    df.columns = ['Days', 'Start', 'End', 'R', 'AR', 'Vol', 'AVol', 'AdjR', 'MDD', 'MDD_Date', 'SR']
    return df


def max_drawdown(vec:pd.DataFrame)->tuple(pd.DataFrame,pd.DataFrame):
    """Obtain max drawdown value and date"""
    maximums = np.maximum.accumulate(vec)
    drawdowns = 1 - vec / maximums
    MDD = np.max(drawdowns)
    MDD_dates = drawdowns.idxmax(axis=0)
    MDD_dates = MDD_dates.apply(lambda x: x.strftime("%Y-%m-%d"))
    return MDD, MDD_dates