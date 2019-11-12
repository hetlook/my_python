import redis


class PageCounter:
    """页面点击计数"""
    def __init__(self, host='localhost', port=6379):
        self.client = redis.StrictRedis(host, port)

    def count_page(self, page='home'):
        """页面点击计数"""
        self.client.incr(page)

    def query_page(self, page='home'):
        """获取页面点击计数"""
        try:
            count = self.client.get(page)
            print('点击次数', int(count))
            return {"click":int(count)}
        except Exception as e:
            print(f'没有人来过{page}页面...')
            return 0