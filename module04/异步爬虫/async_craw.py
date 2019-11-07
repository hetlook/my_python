
# 添加命令行命令，可以通过直接同过参数执行（至少有帮助和url连个选项）

import json
import re
import time
import csv
import sys
import aiohttp
import asyncio
from functools import wraps
import log_func
from aiomultiprocess import Pool
from asyncio import AbstractEventLoop
from concurrent.futures import ProcessPoolExecutor, as_completed

log = log_func.wang_log()

class DecoTime:
    """耗时计算"""
    def __init__(self):
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kw):
            str_log = '函数{}开始运行...'.format(func.__name__)
            print(str_log)
            t1 = time.time()
            func(*args, **kw)
            t = time.time() - t1
            print(f'运行{func.__name__}共用时{int(t)}秒')
        return wrapper

class Crawler:
    """爬取页面的url"""
    def __init__(self, url):
        self.url = url

    def save_url(self, file_name, all_list):
        """存储url"""
        try:
            with open(file_name, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(all_list)
            return {'status': 0, 'statusText': 'saved'}
        except Exception as e:
            print(e)
            return {'status': 1, 'statusText': 'error'}

    async def fetch(self, client, url):
        """获取网页"""
        async with client.get(url) as resp:
            assert resp.status == 200
            html = await resp.text()
            re_url = re.compile(r'"(https|http.*?)"')
            get_url = re_url.findall(html)
            save_result = self.save_url('url.csv', tuple(get_url))
            log.info(f'{save_result}')
            return html

    async def get_url(self, urls):
        """获取url"""
        async with aiohttp.ClientSession() as client:
            tasks = [self.fetch(client, url) for url in urls]
            await asyncio.gather(*tasks)
        
        
    def run_async_crawler(self):
        """执行爬虫"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_url(self.url))


    async def mult_process(self):
        """进程池控制"""
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            await loop.run_in_executor(pool, self.run_async_crawler)

@DecoTime()           
def main():
    # URLS = ['https://aiohttp.readthedocs.io/en/stable/client_reference.html',
        #     'https://devdocs.io/python~3.7-asynchronous-i-o/',
        #     'http://news.baidu.com/guonei',
        #     'http://news.baidu.com/'
        # # ]
    try:
        re_url = re.compile(r'https|http.*?')
        URLS = []
        url =  input('请输入需要获得网页的url：')
        get_url = re.match(re_url, url)
        # print(get_url)
        if get_url:
            URLS.append(url)
            asyncio.run(Crawler(URLS).mult_process())
        else:
            input('输入url格式有误，请重新输入！')
            sys.exit()
    except Exception as e:
        print(e)
            

if __name__ == '__main__':
    main()

