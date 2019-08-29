# -*- coding: utf-8 -*-
# @Time    : 6/8/2019 2:24 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: driver.py
# @Software: PyCharm

import os
from selenium import webdriver

from web.proxy import Proxy

dir_path = os.path.dirname(os.path.realpath(__file__))

class Driver:

    def __init__(self):
        try:
            self.proxy = Proxy()
        except:
            pass


    def chromedriver(self, activate_proxy=False):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--headless")
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument("--disable-dev-shm-usage")
        if activate_proxy:
            proxy = self.proxy.__next__()
            chromeOptions.add_argument("--proxy-server=http://{}".format(proxy))
        driver = webdriver.Chrome(executable_path=f'{dir_path}/webdriver/chromedriver', options=chromeOptions)
        return driver