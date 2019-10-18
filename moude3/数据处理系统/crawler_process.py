#!/usr/bin/env Python
# -*- coding:utf-8 -*-
# 获取信息 + 保存为csv

import json
import re
import time
from urllib.parse import urlparse
from datetime import datetime, timedelta
import csv
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import log_func


class Throttle:
    """阀门类，对相同域名的访问添加延迟时间，避免访问过快
    """
    def __init__(self, delay):
        # 延迟时间，避免访问过快
        self.delay = delay
        # 用字典保存访问某域名的时间
        self.domains = {}
        
    def wait(self, url):
        """对访问过的域名添加延迟时间
        """
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()

class Downloader:
    """下载类，根据url返回内容
    """
    def __init__(self, headers=None, num_retries=3, proxies=None, delay=2, timeout=30):
        self.headers = headers
        self.num_retries = num_retries
        self.proxies = proxies
        self.throttle = Throttle(delay)
        self.timeout = timeout
        self.loger = log_func.wang_log()


    def download(self, url, is_json=False):
        """下载页面"""
        self.loger.info('下载页面:')
        self.loger.info(url)
        self.throttle.wait(url)
        try:
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=self.timeout)
            print(response.status_code)
            if response.status_code == 200:
                if is_json:
                    return response.json()
                else:
                    return response.content
            return None
        except RequestException as e:
            print('error:', e.response)
            html = ''
            if hasattr(e.response, 'status_code'):
                code = e.response.status_code
                print('error code:', code)
                if self.num_retries > 0 and 500 <= code < 600:
                    # 遇到5XX 的错误就重试
                    html = self.download(url)
                    self.num_retries -= 1
            else:
                code = None
        return html

class Recorder:
    """记录类，根据不同保存类型使用相应方法。
    通过类对象使用回掉函数方式直接调用
    """
    def __init__(self, save_type='csv'):
        self.save_type = save_type

    def __call__(self, filename, fields, all_list):
        if hasattr(self, self.save_type):
            func = getattr(self, self.save_type)
            return func(filename, fields, all_list)
        else:
            return {'status': 1, 'statusText': 'no record function'}

    def csv(self, filename, fields, all_list):
        """保存csv"""
        try:
            with open(filename, 'a', newline='') as f:
                writer = csv.writer(f)
                # fields = ('id', '名称', '价格', '评价人数', '好评率')
                writer.writerow(fields)
                for row in all_list:
                    writer.writerow(row)
            return {'status': 0, 'statusText': 'csv saved'}
        except Exception as e:
            print(e)
            return {'status': 1, 'statusText': 'csv error'}

class ItemCommentSpider:
    """抓取商品评价信息
    """
    def __init__(self, headers=None, num_retries=3, proxies=None, delay=2, timeout=30):
        self.headers = headers
        self.num_retries = num_retries
        self.proxies = proxies
        self.throttle = Throttle(delay)
        self.timeout = timeout
        self.download = Downloader(headers, num_retries, proxies, delay, timeout)
        self.loger = log_func.wang_log()    

    def get_comment(self, url, data_list=None):
        """获取评论内容"""
        page = self.download.download(url, is_json=False)
        soup = BeautifulSoup(page, 'lxml')
        self.loger.debug(url)
        title = soup.find('a', attrs={'id':"productName"}).get('title')
        self.loger.debug(title)
        comment_lists = soup.find_all('div', attrs={'style':"position:relative;"})
        if not data_list:
            data_list = []
        for comment in comment_lists:
            row = []
            row.append(title)
            content = comment.find('p', attrs={'class':'body-content'}).text
            self.loger.debug(content)
            row.append(content)
            time = comment.find('div', attrs={'class':'date l'}).find('span').text
            self.loger.debug(time)
            row.append(time)
            data_list.append(row)

        page_num = re.compile(r'.*(\d)-bad.htm').findall(url)[0]
        self.loger.info(f'完成第{page_num}页')


        good_num = soup.find('li',attrs={'data-type':'good'}).get('data-num')
        next_page1 = soup.find('a', attrs={'class':'next rv-maidian next-disable'})
        if int(good_num) > 0 and (next_page1 == None):
            next_page = soup.find('a', attrs={'class':'next rv-maidian'}).get('href')
            self.loger.debug(next_page)
            if next_page != '###':
                next_url = 'https:' + next_page
                self.loger.debug(next_url)
                self.get_comment(next_url, data_list)
        return data_list

    def fetch_data(self, url, filename, callback=None):
        """获取数据"""
        all_list = self.get_comment(url)
        if callback:
            callback(filename, ('商品名', '评论内容', '评论时间'), all_list)

def main():
    headers = {
        'User-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        "referer": "https://suning.com"
        } 
    url = 'https://review.suning.com/cluster_cmmdty_review/general-30499551-000000000608351367-0000000000-1-bad.htm'
    spider = ItemCommentSpider(headers=headers)
    spider.fetch_data(url, 'camera.csv', Recorder('csv'))


if __name__ == '__main__':
    main()