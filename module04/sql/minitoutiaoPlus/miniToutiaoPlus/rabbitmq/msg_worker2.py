# msg_worker.py
# 接受消息，订阅/发布
import time
from basemq import WangMQ
from toutiao_sql import DataManage


class WorkerMQ(WangMQ):
    def __init__(self):
        super().__init__()
        self.dm = DataManage()

    def callback(self, ch, method, properties, body):
        # 接受，消费信息
        print(f"收到消息：{body.decode()}")
        time.sleep(body.count(b"-"))
        print('ok')
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
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
    mq_con = WorkerMQ()
    exchange = mq_con.get_exchange()
    mq_con.make_exchange(exchange=exchange, exchange_type='fanout')
    q_name = mq_con.make_random_queue()
    mq_con.bind_queue(q_name, exchange)
    mq_con.consume(mq_con.callback, q_name)

if __name__ == "__main__":
    main()