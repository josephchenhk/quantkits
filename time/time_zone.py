# -*- coding: utf-8 -*-
# @Time    : 17/9/2019 6:17 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: time_zone.py
# @Software: PyCharm

from datetime import datetime
import pytz

# get datetime of specified local time zone
def local_time(tz='Asia/Hong_Kong'):
	'''
	https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones
	'''
	return datetime.now(pytz.timezone(tz))