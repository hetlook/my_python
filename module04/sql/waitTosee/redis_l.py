import redis

class PageCounter:
    """页面点击计数"""
    def __init__(self, host='192.168.83.129', port=6379):
        self.client = redis.StrictRedis(host, port, password='py8888')
    def set_content(self, name, value):
        """保存数据到redis"""
        self.client.hmset(name, {'age':'22',})
        return 'ok'
        
    def get_content(self, name):
        """取数据从redis"""
        result = self.client.hgetall(name)
        return result


PC = PageCounter()
PC.set_content('wangshuai', 'lsdfsadfdsafasdf')
result = PC.get_content("wangshuai")

print(result)