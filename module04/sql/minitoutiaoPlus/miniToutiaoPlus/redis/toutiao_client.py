# toutiao.py
# 订阅频道，接受订阅频道发布的内容

import redis
from toutiao_sql import DataManage


def subscribe():
    """订阅频道"""
    try:
        dm = DataManage()
        channels = dm.query_author()
        print(channels)
        channel_sub = input("请输入要订阅的channel：")
        if channel_sub in channels:
            client = redis.StrictRedis()
            client_sub = client.pubsub()
            client_sub.subscribe(channel_sub)
            show_msg(client_sub)
        else:
            print("输入的频道不存在！")
    except Exception as e:
        print(e)


def show_msg(sub_obj):
    """显示信息"""
    for msg in sub_obj.listen():
        if msg["type"] == "message":
            print(f'get content: {msg["data"].decode()} from {msg["channel"].decode()}')


def main():
    
    subscribe()

if __name__ == "__main__":
    main()
