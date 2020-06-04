# -*- coding: utf-8 -*-
# @Time    : 29/4/2020 10:07 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: __init__.py.py
# @Software: PyCharm

import os
import logging

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Log等级总开关

# 第二步，创建一个handler，用于写入日志文件
if "log" not in os.listdir():
    os.mkdir(os.path.join(os.getcwd(),"log"))
logfile = './log/logger.txt'
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

# 第三步，再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # 输出到console的log等级的开关

# 第四步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 第五步，将logger添加到handler里面
logger.addHandler(fh)
logger.addHandler(ch)

# 日志
# logger.debug('this is a logger debug message')
# logger.info('this is a logger info message')
# logger.warning('this is a logger warning message')
# logger.error('this is a logger error message')
# logger.critical('this is a logger critical message')



def reset_logger(*args, stream_handler=True, stream_handler_level=logging.DEBUG, **kwargs):
    """
    Overwrite the logger settings.
    :param args:
    :param stream_handler: default using stream handler
    :param stream_handler_level: default setting debug mode
    :param kwargs: should pass something like "file_handler1, file_handler1_level, file_handler2, file_handler2_level"...
    :return: updated logger according to instructions
    """
    # Remove existing handlers
    for hdlr in logger.handlers[:]:  # remove all old handlers
        logger.removeHandler(hdlr)

    # Process file handlers
    params = kwargs.keys()
    handler_levels = [k for k in params if "level" in k]
    handler_params = set(params) - set(handler_levels)
    handlers = [k for k in handler_params if "file_handler" in k]

    fhs = {}
    for h in handlers:
        fh = logging.FileHandler(kwargs[h], encoding='utf-8')
        fh.setLevel(logging.DEBUG)  # set default level to debug
        fhs[h] = fh

    for hl in handler_levels:
        h = hl.replace("_level", "") # get corresponding handler
        if h in fhs:
            fhs[h].setLevel(kwargs[hl]) # if level is specified, update it

    # Process stream handler
    sh = logging.StreamHandler()
    sh.setLevel(stream_handler_level)

    # Set handlers' format (the formatter is given and can not be changed)
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(name)s - %(levelname)s: %(message)s')
    for fh in fhs.values():
        fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    # Add handlers to logger
    for fh in fhs.values():
        logger.addHandler(fh)
    if stream_handler:
        logger.addHandler(sh)