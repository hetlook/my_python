# _*_ coding:utf-8 _*_
# http_server.py

import socket
import re

from admin import DataManage
from redis_test import PageCounter

HOST = ''
PORT = 8888
ADDR = (HOST, PORT)
BUFFSZIE = 1024
# 新建socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 相关参数
# 绑定地址
sock.bind(ADDR)
# 监听连接的个数
sock.listen(1)
print('启动http服务')
flag=1
# 循环发送和接受数据

try:
    while True:
        # 等待连接
        print('等待连接')
        conn, addr = sock.accept()
        print('成功连接：', addr)
        data = conn.recv(BUFFSZIE)
        pagec = PageCounter()
        flag += 1
        if flag>20:
            break
        if data:
            req_path = data.decode('utf-8').splitlines()[0]  
            print('收到数据第一行：', req_path)
            method, path, http = req_path.split()
            paths = re.split('/', path)
            print(paths)
            if paths[1] == 'article':
                if paths[2] == 'all':
                    print(f'切换url路径到{path}')
                    result = DataManage().query_article_all()
                    print(result)
                    pagec.count_page(path)
                    click_num = pagec.query_page(path)
                else:
                    print(f'切换url路径到{path}')
                    pagec.count_page(path)
                    click_num = pagec.query_page(path)
                    result = DataManage().query_article_id(int(paths[2]))
                    print(result)
            
            response = f"""HTTP/1.1 200 OK

            {result}
            {click_num}
            """.encode('gbk')   
            conn.sendall(response) 
        conn.close()
    sock.close()
except Exception as e:
    print(e)