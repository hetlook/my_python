#!/usr/bin/env Python
# -*- coding:utf-8 -*-
# 获取信息 + 保存为csv

import json
import re
from datetime import datetime
import requests
from requests.exceptions import RequestException
import log_func

log = log_func.wang_log()


class Downloader:
    """下载类，根据url返回内容
    """
    def __init__(self, headers=None, num_retries=3, proxies=None, timeout=30):
        self.headers = {
        'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
        "referer": "http://news.iciba.com/views/dailysentence/daily.html"
        }
        self.num_retries = num_retries
        self.proxies = proxies
        self.timeout = timeout

    def download(self, url='http://sentence.iciba.com/index.php?&c=dailysentence&m=getdetail&title=2019-11-15&_=1573811833104', is_json=False):
        """下载页面"""
        log.info('下载页面:')
        log.info(url)
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



class ItemCommentSpider:
    """抓取商品评价信息
    """
    def __init__(self, headers=None, num_retries=3, proxies=None, timeout=30):
        self.headers = headers
        self.num_retries = num_retries
        self.proxies = proxies
        self.timeout = timeout
        self.download = Downloader(headers, num_retries, proxies, timeout)
            
    def get_comment(self, url, data_list=None):
        """获取评论内容"""
        page = self.download.download(url, is_json=True)
        content_en = page['content']
        content_ch = page['note']
        result = []
        result.append(content_en)
        result.append(content_ch)
        return result

def main():
    headers = {
        'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
        "referer": "http://news.iciba.com/views/dailysentence/daily.html"
        } 
    url = 'http://sentence.iciba.com/index.php?&c=dailysentence&m=getdetail&title=2019-11-15&_=1573811833104'
    spider = ItemCommentSpider(headers=headers)
    spider.get_comment(url)

if __name__ == '__main__':
    main()