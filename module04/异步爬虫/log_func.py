#!/usr/bin/env Python
# -*- coding:utf-8 -*-
# log_4_func.py
# log的工程应用
# author: De8uG

import logging

"""
工程使用需求：
1-不同日志名称
2-打印同时在控制台，也有文件
3-灵活控制等级
"""



def wang_log(logger_name='WANG-LOG', log_file='wang.log', level=logging.INFO):
    # 创建 logger对象
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)  # 添加等级

    # 创建控制台 console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # 创建文件 handler
    fh = logging.FileHandler(filename=log_file, encoding='utf-8')

    # 创建 formatter
    formatter = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)d] %(name)s %(levelname)s %(message)s')

    # 添加 formatter
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # 把 ch， fh 添加到 logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def main():
    # 测试
    logger = wang_log()
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')

if __name__ == '__main__':
    main()
