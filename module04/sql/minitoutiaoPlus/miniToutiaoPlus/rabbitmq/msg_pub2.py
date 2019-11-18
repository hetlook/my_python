# msg_pub.py
# 发送消息， 订阅/发布

import sys
from basemq import WangMQ
from toutiao_sql import DataManage

class PubMQ(WangMQ):
    def __init__(self):
        super().__init__()
        self.dm = DataManage()

    def get_content(self):
        """获得文章内容"""
        titles = self.dm.show_all_article_title()
        print(titles)
        title = input("请输入需要发布的文章title：")
        content = self.dm.query_article_by_title(title)
        return content

    def get_exchange(self):
        """获得exchange"""
        channels = self.dm.query_author()
        print("channels:", channels)
        channel = input("请输入channel：")
        if channel in channels:
            return channel
        else:
            print("输入的订阅频道错误！")



def main():
    mq_pub = PubMQ()
    msg = mq_pub.get_content()
    exchange = mq_pub.get_exchange()
    mq_pub.make_exchange(exchange=exchange, exchange_type='fanout')
    # mq_pub.make_queue('super-queue')
    mq_pub.publish(msg, exchange)
    print(f"发布文章：", msg)

if __name__ == "__main__":
    main()
