import redis
from datetime import datetime
from dateutil.relativedelta import relativedelta

time = '2019-11-14 14:22'

client = redis.StrictRedis(host='192.168.83.129', port=6379, password='py8888')
key_list = client.keys()

def get_content(time, num):
    """get 数据"""
    i = 0
    count = 0
    result_list = []
    for key in key_list:
        if count < num:
            temp = datetime.strptime(time, '%Y-%m-%d %H:%M') + relativedelta(minutes=i)
            i += 1
            temp = temp.strftime('%Y-%m-%d %H:%M')
            h = client.hgetall(temp)
            if h:
                result_list.append(h)
                count += 1  
    # print(count)
    # print(result_list)  
    if count < num:
        print("索取数据超出范围")

    # return(result_list)
    for x in result_list:
        en = x[b'en'].decode()
        ch = x[b'ch'].decode()
        time = x[b'time'].decode()
        print(en, ch, time)

print(get_content(time, 2))