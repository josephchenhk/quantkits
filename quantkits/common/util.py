# -*- coding: utf-8 -*-
# @Time    : 17/9/2019 6:24 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: util.py
# @Software: PyCharm
import os
from typing import Sequence


def verify_lang(lang):
	"""Ensure language is either en or cn"""
	assert lang in ('en', 'cn'), "Parameter `lang` should be either `en` or `cn`, got `{}` instead.".format(lang)

def check_table_exists(dbcon, dbname, tablename):
	"""Check whether a table exists or not"""
	result = dbcon.execute("""
							SELECT COUNT(*)
							FROM information_schema.tables
							WHERE TABLE_SCHEMA = '{0}' 
							AND TABLE_NAME = '{1}'
							""".format(
							dbname.replace('\'', '\'\''),
							tablename.replace('\'', '\'\'')
							)
	)
	if result.fetchone()[0] == 1:
		return True
	return False


def underscore_to_pascalcase(value):
	"""Convert abc_def to AbcDef"""
	def pascalcase():
		yield str.capitalize
		while True:
			yield str.lower
	ret = ""
	for x in value.split("_"):
		c = pascalcase()
		ret += c.__next__()(x)
	return ret

def pascalcase_to_underscore(value):
	"""Convert AbcDef to abc_def"""
	def underscore():
		while True:
			yield str.lower
	u = underscore()
	ret = ""
	for x in value:
		if x.isupper():
			ret += "_"
		ret += u.__next__()(x)
	return ret[1:]

def get_files_path(pattern:str, search_folder=os.getcwd())->Sequence[str]:
	"""Search a folder, and return all abolute paths of files that match specified pattern"""
	files = []
	for dirpath, subdirs, files in os.walk(search_folder):
		for x in files:
			if pattern in x: # for example, pattern = ".jpg"
				files.append(os.path.join(dirpath, x))
	return files