# -*- coding: utf-8 -*-
# @Time    : 6/8/2019 2:24 PM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: driver.py
# @Software: PyCharm

import os
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from quantkits.web.proxy import Proxy



class Driver:


    def __init__(self):
        pass

    def chromedriver(self, activate_proxy=False):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--headless")
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument("--disable-dev-shm-usage")
        if activate_proxy:
            self.proxy = Proxy()
            proxy = self.proxy.__next__()
            chromeOptions.add_argument("--proxy-server=http://{}".format(proxy))

        # Windows
        # chromeOptions.add_argument('--disable-gpu')  # For windows this is necessary
        # driver = webdriver.Chrome(executable_path=f'{dir_path}/webdriver/chromedriver.exe', options=chromeOptions)

        # Mac
        # driver = webdriver.Chrome(executable_path=f'{os.getcwd()}/crawler/webdriver/chromedriver_mac', options=chromeOptions)

        # Remote
        driver = webdriver.Remote(
            command_executor='http://api.atabet.com:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX
        )

        return driver