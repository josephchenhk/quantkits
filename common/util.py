# -*- coding: utf-8 -*-
# @Time    : 17/9/2019 6:24 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: util.py
# @Software: PyCharm

def verify_lang(lang):
	assert lang in ('en', 'cn'), "Parameter `lang` should be either `en` or `cn`, got `{}` instead.".format(lang)

def check_table_exists(dbcon, dbname, tablename):
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