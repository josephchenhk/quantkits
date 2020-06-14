# -*- coding: utf-8 -*-
# @Time    : 29/4/2020 11:38 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: decorators.py
# @Software: PyCharm
import traceback
from functools import wraps, partial
from datetime import datetime
import time

RETRY_NUMBER = 5
RETRY_WAITING_TIME = 5.3


def timeit(func):
	"""Measure execution time of a function"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		tic = datetime.now()
		res = func(*args, **kwargs)
		toc = datetime.now()
		print("{} Elapsed time: {} seconds".format(func.__name__, (toc - tic).seconds))
		return res
	return wrapper


def safe_return(func):
	"""Always ensure a valid return"""
	@wraps(func)
	def func_wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as e:
			traceback.print_exc()
			return None
	return func_wrapper


def retry(func=None, *, number=RETRY_NUMBER, waiting_time=RETRY_WAITING_TIME):
	"""
	Retry a function for specified number and waiting time; if no parameters are passed into, default values will be used.
	:param func:
	:param number:
	:param waiting_time:
	:return:
	"""
	if func is None:
		return partial(retry, number=number, waiting_time=waiting_time)

	@wraps(func)
	def func_wrapper(*args, **kwargs):
		for n in range(number):
			try:
				return func(*args, **kwargs)
			except Exception as e:
				traceback.print_exc()
				print("{}. Retry after {} seconds.".format(e, waiting_time))
				time.sleep(waiting_time)
		raise ConnectionError("Requests are rejected too many times.")
	return func_wrapper

# Example to use decorators
# @safe_return
@retry
def div(a, b):
	return a/b

if __name__=="__main__":
	print(div(3, 0))