# -*- coding:utf-8 -*-
# 51memo_object_oriented.py
# A memo demo 51备忘录 , 面向对象
# author :wang

import os
import pickle
import datetime

import re
import configparser
from docx import Document
from io import StringIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

base_dir = os.getcwd()


class Memo:
    "进行数据格式存储"
    def __init__(self, name='', thing='', date=''):
        self._id = 0
        self.name = name
        self.thing = thing
        self.date = date 
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, num):
        self._id = num + 1

class MemoAdmin:
    "进行Memo的增删改查，处理输出输出"
    def __init__(self, file_name):
        self.file_name = file_name
        self.memo_list = []

    def add(self):
        "添加一条memo"
        name = input('姓名：').strip()
        thing = input('事件：').strip()
        date = input('日期：').strip()
        date = datetime.datetime.strptime(date, '%Y/%m/%d')
        one = Memo(name, thing, date)
        b = self.load()
        if len(b) == 0:
            one.id2 = 0  # =>@id.setter
        else:
            one.id = b[-1].id
        self.memo_list.append(one)
        self.save(self.memo_list)
        print('完成添加，请继续其他操作！')
        
    def delete(self):
        "删除一条memo"
        mod_id = input('请输入要删除的id号：')
        b = self.load()
        try:
            for x in b:
                if x.id == int(mod_id):
                    b.pop(x)
                    self.save(b)
                    print('完成删除，请继续其他操作！')                   
        except Exception as f:
            print(f)

    def modify(self):
        "修改一条memo"
        mod_id = input('请输入要更改的id号：')
        b = self.load()
        try:
            for x in b:
                if x.id == int(mod_id):
                    x.name = input('姓名：').strip()
                    x.thing = input('事件：').strip()
                    x.date = input('日期：').strip()
                    x.date = datetime.datetime.strptime(x.date, '%Y/%m/%d')
                    self.save(b)
                    print('完成更改，请继续其他操作！')
        except Exception as f:
            print(f)
    
    def query(self):
        "查询memo"
        mod_id = input('请输入要查询的id号：')
        b = self.load()
        try:
            for x in b:
                if x.id == int(mod_id):
                    print(f'查询结果 id:{x.id}, name:{x.name}, thing:{x.thing}, date:{x.date}')
        except Exception as f:
            print(f)

    def save(self, memo_list, file_name):
        "保存" 
        with open(file_name, 'wb') as f:
            pickle.dump(memo_list, f)

    def load(self):
        "加载并显示所有的memo"

        data = []
        if os.path.exists('db.pkl'):
            with open('db.pkl', 'rb') as f:
                data = pickle.load(f)
        else:
            with open('db.pkl', 'wb') as f:
                pickle.dump(data, f)
        for x in data:
            print(f'id:{x.id}, name:{x.name}, thing:{x.thing}, date:{x.date}')
        return data

    def export_to_pdf(self):
        """
        将历史数据导出到pdf，文件导出功能
        from_name: 数据来源文件名
        go_name: 数据导出文件名
        """
        pdf_list = []
        data = self.load()
        for x in data:
            pdf_list.append(f'id:{x.id}, name:{x.name}, thing:{x.thing}, date:{x.date}')
        pdf_obj = ExportPDF(pdf_list, 'history.pdf')
        pdf_obj.save_string()

    def logical_control(self, admin):
        "流程控制Logical Control "
        while True:
            print('请选择需要进行的操作')
            menu = {
                '1':'add',
                '2':'delete',
                '3':'modify',
                '4':'query',
                '5':'save',
                '6':'load',
                '7':'export_to_pdf',
                '0':'quit'
            }
            for k,v in menu.items():
                print(k, v)
            try:
                choose = input('请输入需要选择的操作编号：')           
                if choose == '0':
                    print('退出！' )
                    break
                else:
                    func = getattr(admin, menu[choose])
                    if (func):
                        func()
                    else:
                        print('没这个操作！')
                        continue
            except Exception as f:
                print("输入有误请重新输入")

class ExportPDF:
    """
    Export a pdf file based on reportlab
    把要处理的文本result_list写成pdf文件
    """
    def __init__(self, result_list, output_path, is_custom_color=False, color=(0.77, 0.77, 0.77), font_size=8, offset_x=5, offset_y=5):
        self.result_list = result_list
        self.output_path = output_path
        self.is_custom_color = is_custom_color
        self.font_size = font_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.fonturl = os.path.join(base_dir,'SimSunb.ttf')
        pdfmetrics.registerFont(TTFont('SimSunb', self.fonturl))  # 导入字体文件，使用Windows字体或下载好的"simsun.ttf"，用来显示中文

    def save_string(self):
        """使用canvas把数据绘制到pdf文件，默认坐标从左下角开始，与屏幕坐标（右上角开始）相反，所以需要单独处理
        """
        c = canvas.Canvas(self.output_path, pagesize=A4)
        width, height = A4  # 使用默认的A4大小

        if self.is_custom_color:
            c.setFillColorRGB(color)  # 需要单独设置颜色时候使用

        new_height = height
        for line in self.result_list:
            c.setFont("SimSunb", self.font_size)  # 处理中文字体
            # 写入每一行的数据，每一行的y坐标需要单独处理，这里用总高度减去偏移量和字体高度，使得每一行依次写入文件
            new_height = new_height - self.offset_y - self.font_size
            print('write data: ', self.offset_x, new_height, line)
            c.drawString(self.offset_x, new_height, line)

        c.showPage()
        c.save()

    def save_text(self):
        """使用canvas把数据绘制到pdf文件，
        这是另一种写法，通过文本的方式写入，只需要定义原始写入坐标
        """
        c = canvas.Canvas(self.output_path, pagesize=A4)
        width, height = A4  # 使用默认的A4大小

        if self.is_custom_color:
            c.setFillColorRGB(color)  # 需要单独设置颜色时候使用

        c.setFont("SimSunb", self.font_size)  # 处理中文字体
        obj = c.beginText()  # 生成text对象
        obj.setTextOrigin(10, height-self.offset_y*20)  # 第一次写入位置，坐标自定义,注意高度需要调整
        for line in self.result_list:
            print('write data: ', line)
            obj.textLine(line)  # 写入文件

        c.drawText(obj)
        c.showPage()
        c.save()

class LogRegCon:
    """登陆注册"""
    def __init__(self):
        pass

    def login(self):
        "登陆"
        user_list = []
        with open('users1.pkl', 'rb') as f:
            while True:
                try:
                    data = pickle.load(f)
                    user_list.append(data)
                    # print(data)
                except Exception as f:
                    break
        user_name = input('请输入用户名:')
        password = input('请输入密码:')
        index = 1
        for x in user_list:
            if x['user_name'] == user_name:
                if x['password'] == password:
                    print('登陆成功！')
                    index = 0
                    config = configparser.ConfigParser()
                    config.read('common.ini')
                    file_name = config[user_name]['file_path']
                    # print(file_name)
                    return file_name
                else:
                    print('密码错误！请重新输入')
                    self.login()
        if index == 1:
            print("用户不存在")
            self.log_control() 
   
    def register(self):
        "注册"
        user_info = {}
        user_info['user_name'] = input('请输入用户名:')
        user_info['password'] = input('请输入密码:')
        # print(user_info)
        with open('users1.pkl','ab') as f:
            pickle.dump(user_info, f)
        self.add_config(user_info['user_name'], base_dir)
            
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

    def log_control(self):
        "登陆提示"
        admin = LogRegCon()
        while True:
            print('欢迎使用过51备忘录！')
            menu = {
                '1': 'login',
                '2': 'register',
                '0': 'quit'
            }
            for k, v in menu.items():
                print(k, v)
            choose = input('请输入需要选择的编号：')
            if choose == '0':
                print('退出！')
                break
            else:
                func = getattr(admin, menu[choose])

                if (func):
                    f = func()
                    if f:
                        return(f)
                else:
                    print('没有这个操作！')
                    continue

def main():
    l = LogRegCon()
    l_return = l.log_control()
    
    if len(l_return) > 0:
        admin = MemoAdmin(l_return)
        admin.logical_control(admin)

if __name__ == "__main__":
    main()

