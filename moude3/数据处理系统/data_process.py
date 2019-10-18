# -*- coding:utf-8 -*-
# 简单的数据处理系统，数据抓取，分析，

import os
import sys
import json
import pickle
import configparser
import jsonlines
import office_process
# import crawler_process
import log_func

class LogRegCon:
    """数据梳理系统
    """
    def __init__(self):
        self.base_dir = os.getcwd()
        self.log = log_func.wang_log() 

    def check(self, user_name, password, file_name):
        "检查用户账号密码是否正确"
        user_list = []
        if os.path.exists(file_name):
            with jsonlines.open(file_name) as reader:
                for obj in reader:
                    user_list.append(obj)
            un_num = pw_num = 0
            for x in user_list:
                if x['user_name'] == user_name: 
                    un_num = 1
                    if  x['password'] == password:
                        self.log.warning('登陆成功！')
                        pw_num = 1
                        return 'ok'
            if un_num == 0:
                self.log.info("用户不存在请注册！")
                self.log_control()
            elif un_num == 1 and pw_num == 0:
                self.log.info("密码错误请重新输入！")
                self.log_control()
        else:
            self.log.info("用户不存在先请注册")

    def login(self):
        "登陆"
        self.log.warning('欢迎登陆爬虫系统！')
        user_name = input('请输入用户名:')
        password = input('请输入密码:')
        user_type = input('是否为管理员(admin)用户(user):')
        if user_type == 'admin':
            file_name = 'admin.json'
            if self.check(user_name, password, file_name) == 'ok':
                self.log.debug('欢迎使用管理员操作')
                self.admin_menu()
        elif user_type == 'user':
            file_name = user_name + '.json'
            if self.check(user_name, password, file_name) == 'ok':
                enabled = self.read_json(file_name)['enabled']
                if enabled == 1:
                    self.log.warning('欢迎使用普通用户操作')
                    self.user_menu(user_name)
                if enabled == 0:
                    self.log.warning('用户已被加入黑名单！')
  
    def register(self):
        "注册"
        user_info = {}
        user_info['user_name'] = input('请输入用户名:')
        user_info['password'] = input('请输入密码:')
        user_info['user_type'] = input('是否为管理员(admin)用户(user):')
        if user_info['user_type'] == 'admin':
            user_info['operation'] =  ['crawler', 'office', 'image']
            user_file_name = 'admin.json'
            self.save_admin(user_info, user_file_name)
        elif user_info['user_type'] == 'user':
            user_info['operation'] =  []
            user_file_name = user_info['user_name'] + '.json'
            user_info['enabled'] = 1
            self.write_json(user_info, user_file_name)
        
        self.add_config(user_info['user_name'], self.base_dir)

    def quit(self):
        "退出"
        self.log.info('退出！')
        sys.exit()

    def add_operation(self):
        "给普通用户添加操作授权"
        user_name = input('请输入要添加权限的用户：')
        operation = input('请输入需要添加的权限(crawl,office)：')
        file_name = user_name + '.json'
        d = self.read_json(file_name)
        d['operation'].append(operation) 
        self.write_json(d, file_name)
        self.log.debug(f'权限{operation}添加成功')
    def add_blacklist(self):
        "给普通设置黑名单"
        user_name = input('请输入要设置黑名单的用户名：')
        file_name = user_name + '.json'
        d = self.read_json(file_name)
        d['enabled'] = 0 
        self.write_json(d, file_name)
        self.log.debug(f"添加{user_name}到黑名单成功！")

    def read_json(self, file_name):
        "读json文件"
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                return(json.load(f))
        else:
            self.write_json({},file_name)
            return({})
    
    def write_json(self, data, file_name):
        "写json文件"
        with open(file_name, 'w') as f:
            json.dump(data, f)

    def save_admin(self, data, file_name):
        "保存json数据" 
        with jsonlines.open(file_name, mode='w') as writer:
            writer.write(data)
            self.log.debug("用户信息写入json文件!")
    
    def add_config(self,user_name, base_dir):
        "添加配置文件,为备忘录数据指定路径和文件名"
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        file_name = user_name + '.pkl'
        file_path = os.path.join(base_dir, file_name)  # 备忘录路径
        config.add_section(user_name)
        config.set(user_name,'file_path', file_path)
        config.set(user_name,'file_name', file_name)
        self.save_config(base_dir, config)
        
    def save_config(self,base_dir, config):
        "保存配置文件"
        config_path = os.path.join(base_dir, 'common.ini')  # 配置文件路径
        with open(config_path, 'a') as f:
            config.write(f)

    def crawl(self):
        "爬虫"
        headers = {
        'User-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        } 
        url = 'https://review.suning.com/cluster_cmmdty_review/general-30499551-000000000608351367-0000000000-1-bad.htm'
        spider = crawler_process.ItemCommentSpider(headers=headers)
        spider.fetch_data(url, 'camera.csv', Recorder('csv'))
 
    def office(self):
        "office"
        process = office_process.OfficeOperation().operation()

    def log_diaplay(self, menu, admin):
        "逻辑页面显示操作信息，选择操作"
        while True:
            print('欢迎使用爬虫！')
            for k, v in menu.items():
                print(k, v)
            choose = input('请输入需要选择的编号：')
            func = getattr(admin, menu[choose])
            if (func):
                f = func()
                if f:
                    return(f)
            else:
                print('没有这个操作！')
                continue
  
    def admin_menu(self):
        "管理员界面"
        admin = LogRegCon()
        menu = {
            '1': 'crawl',
            '2': 'office',
            '3': 'add_operation',
            '4': 'add_blacklist',
            '0': 'quit'
        }
        self.log_diaplay(menu, admin)
  
    def user_menu(self, user_name):
        "用户界面"
        admin = LogRegCon()
        file_name = user_name + '.json'
        d = self.read_json(file_name)
        d = d['operation']
        if len(d)== 1:
            menu = {
                '1': 'login',
                '2': 'register',
                '3': d[0],
                '0': 'quit'
            }
            self.log_diaplay(menu, admin)
        elif len(d)== 2:
            menu = {
                '1': 'login',
                '2': 'register',
                '3': d[0],
                '4': d[1],
                '0': 'quit'
            }
            self.log_diaplay(menu, admin)
        elif len(d)== 3:
            menu = {
                '1': 'login',
                '2': 'register',
                '3': d[0],
                '4': d[1],
                '4': d[2],
                '0': 'quit'
            }
            
            self.log_diaplay(menu, admin)
        else:
            self.log_control()        

    def log_control(self, admin):
        "登陆提示"
        
        menu = {
            '1': 'login',
            '2': 'register',
            '0': 'quit'
        }
        while True:
            print('欢迎使用爬虫！')
            for k, v in menu.items():
                print(k, v)
            choose = input('请输入需要选择的编号：')
            func = getattr(admin, menu[choose])
            if (func):
                f = func()
                if f:
                    return(f)
            else:
                print('没有这个操作！')
                continue
        admin = LogRegCon()
        self.log_diaplay(menu, admin)
 
def main():
    admin = LogRegCon()
    l = admin.log_control(admin)
    # l = admin.quit()

if __name__ == '__main__':
    main()




