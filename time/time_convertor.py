# -*- coding: utf-8 -*-
# @Time    : 16/9/2019 5:29 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: time_convertor.py
# @Software: PyCharm

"""
Converting between datetime, timestamp and datetime64
"""
import pandas as pd
import numpy as np
from datetime import datetime

UNIX_EPOCH = np.datetime64(0, 's')
ONE_SECOND = np.timedelta64(1, 's')

def from_datetime64_to_datetime(dt64: np.datetime64)->datetime:
    seconds_since_epoch = (dt64 - UNIX_EPOCH) / ONE_SECOND
    return datetime.utcfromtimestamp(seconds_since_epoch)

def from_datetime64_to_timestamp(dt64: np.datetime64)->pd.Timestamp:
    return pd.Timestamp(dt64)

def from_timestamp_to_datetime(ts: pd.Timestamp)->datetime:
    return ts.to_pydatetime()

def from_timestamp_to_datetime64(ts: pd.Timestamp)->np.datetime64:
    return ts.to_datetime64()