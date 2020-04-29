# -*- coding: utf-8 -*-
# @Time    : 16/9/2019 5:29 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: conversion.py
# @Software: PyCharm

import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta

UNIX_EPOCH = np.datetime64(0, 's')
ONE_SECOND = np.timedelta64(1, 's')

def from_datetime64_to_datetime(dt64: np.datetime64)->datetime:
    """Convert from datetime64 to datetime"""
    seconds_since_epoch = (dt64 - UNIX_EPOCH) / ONE_SECOND
    return datetime.utcfromtimestamp(seconds_since_epoch)

def from_datetime64_to_timestamp(dt64: np.datetime64)->pd.Timestamp:
    """Convert from datetime64 to timestamp"""
    return pd.Timestamp(dt64)

def from_timestamp_to_datetime(ts: pd.Timestamp)->datetime:
    """Convert from timestamp to datetime"""
    return ts.to_pydatetime()

def from_timestamp_to_datetime64(ts: pd.Timestamp)->np.datetime64:
    """Convert from timestamp to datetime64"""
    return ts.to_datetime64()

def from_timestr_to_milliseconds(timestr:str)->int:
    """Convert HH:MM:SS,mmm str to milliseconds(int)"""
    hour_min_sec, millisec = timestr.split(",")
    hour, min, sec = hour_min_sec.split(":")
    hour, min, sec, millisec = int(hour), int(min), int(sec), int(millisec)
    return hour*3600*1000 + min*60*1000 + sec*1000 + millisec

def from_timeperiod_to_relativedelta(period="-6M"):
    """Convert time period to a relativedelta value"""
    if "Y" in period:
        period = period.replace("Y","")
        period = int(period)
        params = {"years":period}
    elif "M" in period:
        period = period.replace("M","")
        period = int(period)
        params = {"months":period}
    elif "D" in period:
        period = period.replace("D", "")
        period = int(period)
        params = {"days": period}
    else:
        raise ValueError("parameter can only be ('Y','M','D').")
    return relativedelta(**params)

def local_time(tz='Asia/Hong_Kong'):
	'''
	Get datetime of specified local time zone
	Ref: https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones
	'''
	return datetime.now(pytz.timezone(tz))

