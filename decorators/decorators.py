# -*- coding: utf-8 -*-
# @Time    : 16/9/2019 6:27 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: decorators.py
# @Software: PyCharm

from functools import wraps, partial
from datetime import datetime
import time

RETRY_NUMBER = 5
RETRY_WAITING_TIME = 5.3

# Measure execution time of a function
def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tic = datetime.now()
        res = func(*args, **kwargs)
        toc = datetime.now()
        print("{} Elapsed time: {} seconds".format(func.__name__, (toc - tic).seconds))
        return res
    return wrapper

# Always ensure a valid return
def safe_return(func):
	@wraps(func)
	def func_wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as e:
			print(e)
			return None
	return func_wrapper

# retry a function for specified number and waiting time;
# if no parameters are passed into, default values will be used.
def retry(func=None, *, number=RETRY_NUMBER, waiting_time=RETRY_WAITING_TIME):
	if func is None:
		return partial(retry, number=number, waiting_time=waiting_time)

	@wraps(func)
	def func_wrapper(*args, **kwargs):
		for n in range(number):
			try:
				return func(*args, **kwargs)
			except Exception as e:
				print("{}. Retry after {} seconds.".format(e, waiting_time))
				time.sleep(waiting_time)
		raise ConnectionError("Requests are rejected too many times.")
	return func_wrapper