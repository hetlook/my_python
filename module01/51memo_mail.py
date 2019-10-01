# -*- coding:utf-8 -*-
# 51memo_object_oriented.py
# A memo demo 51备忘录,查询接口根据月份返回json数据，发送邮件
# author :wang

import os
import pickle
import datetime

from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from dateutil.parser import *
import json

import re
import configparser
from docx import Document
from io import StringIO

import logging

import smtplib
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

base_dir = os.getcwd()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.disable(logging.CRITICAL)


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
        date = TimeMaster().change_datetime_num(date)
        one = Memo(name, thing, date)
        b = self.load(self.file_name)
        print(b)
        if len(b) == 0:
            one.id = 0  # =>@id.setter
        else:
            one.id = b[-1].id
        self.memo_list.append(one)
        self.save(self.memo_list, self.file_name)
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
                    logger.debug('完成删除，请继续其他操作！')                   
        except Exception as f:
            print(f)

    def modify(self):
        "修改一条memo"
        mod_id = input('请输入要更改的id号：')
        b = self.load(self.file_name)
        try:
            for x in b:
                if x.id == int(mod_id):
                    x.name = input('姓名：').strip()
                    x.thing = input('事件：').strip()
                    x.date = input('日期：').strip()
                    x.date = datetime.datetime.strptime(x.date, '%Y/%m/%d')
                    self.save(b)
                    logger.debug('完成更改，请继续其他操作！')
        except Exception as f:
            print(f)
    
    def query(self, time_type, time_num):
        """
        "查询memo"
        time_type:时间类型，year，month,day
        time_num:具体时间
        """
        memo_list = []
        if os.path.exists(self.file_name):
            with open(self.file_name, 'rb') as f:
                data = pickle.load(f)
        else:
            data = []

        if time_type == 'year':
            for x in data:
                a = parse(x.date)
                if a.year == int(time_num):
                    c = {'id':x.id, 'name':x.name, 'thing':x.thing, 'date':x.date}
                    with open(str(time_num) +'年份.json', 'a') as z:
                        json.dump(c, z)
                    memo_list.append(c)
        
        elif time_type == 'month':
            for x in data:
                a = parse(x.date)
                if a.month == int(time_num):
                    c = {'id':x.id, 'name':x.name, 'thing':x.thing, 'date':x.date}
                    with open(str(time_num) +'月份.json', 'a') as z:
                        json.dump(c, z)
                    memo_list.append(c)
       
        elif time_type == 'day':
            for x in data:
                a = parse(x.date)
                if a.day == int(time_num):
                    c = {'id':x.id, 'name':x.name, 'thing':x.thing, 'date':x.date}
                    with open(str(time_num) +'天.json', 'a') as z:
                        json.dump(c, z)
                    memo_list.append(c)
        
        else:
            print('所查询的时间没有待办事项!') 

        return(memo_list)        

    def save(self, memo_list, file_name):
        "保存" 
        with open(file_name, 'wb') as f:
            pickle.dump(memo_list, f)

    def load(self, file_name):
        "加载并显示所有的memo"
        data = []
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                data = pickle.load(f)
        else:
            with open(file_name, 'wb') as f:
                return(data)
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
        data = self.load(self.file_name)
        # print(data)
        for x in data:
            pdf_list.append(f'id:{x.id}, name:{x.name}, thing:{x.thing}, date:{x.date}')
        print(pdf_list)
        pdf_obj = ExportPDF(pdf_list, 'history.pdf')
        pdf_obj.save_string()

            # print(type(pdf))

    def send_memo(self):
        """
        发送那个邮件到指定地址，根据输入内容
        go_mail_addr:目的地址
        time_type:时间类型：year，month，day
        time_num:具体时间
        """
        month = input('查询时间类型year，month，day：')
        num =  input('查询时间：')
        a = self.query(month, num)
        a = str(a)

        mail_master = MailMaster("邮箱授权码")
        mail_master.send_email_all('memo', a)

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
                '8':'send_memo',
                '0':'quit'
            }
            for k,v in menu.items():
                print(k, v)
            # try:
            #     choose = input('请输入需要选择的操作编号：')           
            #     if choose == '0':
            #         print('退出！' )
            #         break
            #     else:
            #         func = getattr(admin, menu[choose])
            #         if (func):
            #             func()
            #         else:
            #             print('没这个操作！')
            #             continue
            # except Exception as f:
            #     # print("输入有误请重新输入")
            #     print(f)
        
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
        user_name = input('请输入用户名:')
        password = input('请输入密码:')
        if os.path.exists('users1.pkl'):
            with open('users1.pkl', 'rb') as f:
                while True:
                    try:
                        data = pickle.load(f)
                        user_list.append(data)
                        print(data)
                    except Exception as f:
                        break
            index = 1
            for x in user_list:
                if x['user_name'] == user_name:
                    if x['password'] == password:
                        print('登陆成功！')
                        index = 0
                        config = configparser.ConfigParser()
                        config.read('common.ini')
                        file_name = config[user_name]['file_path']
                        print(file_name)
                        # print(config.sections())
                        return file_name
                    else:
                        print('密码错误！请重新输入')
                        self.login()
            if index == 1:
                print("用户不存在")
                self.log_control() 
        else:
            print("用户不存在先请注册")
            self.register()
   
    def register(self):
        "注册"
        user_info = {}
        user_info['user_name'] = input('请输入用户名:')
        user_info['password'] = input('请输入密码:')
        print(user_info)
        with open('users1.pkl','ab') as f:
            pickle.dump(user_info, f)
        self.add_config(user_info['user_name'], base_dir)
            
        # try:
        #     user_info = {}
        #     user_info['user_name'] = input('请输入用户名:')
        #     # # 判断你用户名格式是否正确
        #     # re_user_name = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{4,15}$')
        #     # match = re_user_name.match(user_info['user_name'])
        #     # if match:
        #     #     print('帐号不合法(字母开头，允许5-16字节，允许字母数字下划线)！')
        #     #     register()
        #     user_info['password'] = input('请输入密码:')
        #     # # 判断密码格式是否正确
        #     # re_password = re.compile(r'^[a-zA-Z]\w{5,17}$')
        #     # match = re_password.match(user_info['password'])
        #     # if match == user_info['password']:
        #     #     print('密码不合法(以字母开头，长度在6~18之间，只能包含字母、数字和下划线)！')
        #     #     register()
            
        #     # print(user_info['user_name'])
        #     # users_list.append(user_info)
        #     with open('users.pkl','a') as f:
        #         pickle.dumps(user_info, f)
        # except Exception as f:
        #     print(f)

    def add_config(self,user_name, base_dir):
        "添加配置文件,为备忘录数据指定路径和文件名"
        # config = configparser.ConfigParser()
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        file_name = user_name + '.pkl'
        # base_dir = 'C:\PythonLearn\code\module-3\work',
        file_path = os.path.join(base_dir, file_name)  # 备忘录路径
        
        
        #     方法一：写配置
        #     config[user_name] = {}
        #     config[user_name]['file_path'] = file_path
        #     config[user_name]['file_name'] = file_name
        # else:
        # 方法二：写配置
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
            # try:
            # except Exception as f:
            #     # print("输入有误请重新输入！")
            #     print(f)

class TimeMaster:
    """时间格式管理类"""
    def __init__(self, fmt='%Y-%m-%d %X'):
        self.output_format = fmt

    def change_datetime(self, dt):
        '''转换格式为xxxx/xx/xx xx/xx/xx的时间'''
        my_time = parser.parse(dt)
        # date_str = date1.strftime('%Y-%m-%d %X')
        now = datetime.now()
        return(now, my_time.strftime(self.output_format))  # 返回多个，返回为元组，使用可用多个变量接收：now, date_str = change_datetime(dt)

    def change_datetime_cn(self, dt):
        '''转换中文年月日的时间'''
        date1 = dt.replace('年', '/').replace('月', '/').replace('日', '')  # 多级替换，每集替换后又是一个新的对象，提供给下一个替换
        return(self.change_datetime(date1))

    def change_datetime_num(self,dt):
        '''转换'1.5'这种月日格式的日期， 并添加时间'''
        month, day = dt.split('.')  # 接收多个变量的格式
        now = datetime.now()  # 当前时间
        my_time = now.replace(day=int(day), month=int(month))  # 实时间是int
        print(my_time, type(my_time))
        # return(now, my_time.strftime(self.output_format))
        return(my_time.strftime(self.output_format))

class MailMaster:
    """邮箱大师"""
    def __init__(self, password, smtp_server='smtp.qq.com', email_addr=''):
        self.smtp = SMTP_SSL(smtp_server)
        # smtp.set_debuglevel(1)
        self.smtp.ehlo(smtp_server)
        self.smtp.login(email_addr, password)
        self.email_from = email_addr
        self.email_to = [""]

    def add_email_to_list(self, addr):
        self.email_to.append(addr)

    def notice(self, username, text, subject='通知信息'):
        self.send_email_all(subject, f'{username}\n' + text)

    def send_email_all(self, subject, body, mailtype='plain', attachment=None):  
        """  发送邮件通用接口
        subject: 邮件标题
        body: 邮件内容
        mailtype： 邮件类型，默认是文本，发html时候指定为html
        attachment： 附件
        """
        msg = MIMEMultipart()  # 构造一个MIMEMultipart对象代表邮件本身

        msg["Subject"] = Header(subject, "utf-8")
        msg["from"] = self.email_from

        # try:  
        #     if len(self.email_to) > 0:
        #         to_mail = self.email_to  
        #         msg['To'] = ','.join(to_mail)
        #     else:
        #         raise NoMailListError('还没添加发送人呢，使用add_email_to_list进行填加')

        #     # mailtype代表邮件类型，纯文本或html等
        #     msg.attach(MIMEText(body, mailtype, 'utf-8'))  

        #     # 有附件内容，才添加到邮件
        #     if attachment:
        #         # 二进制方式模式文件  
        #         with open(attachment, 'rb') as f:  
        #             # MIMEBase表示附件的对象  
        #             mime = MIMEBase('text', 'txt', filename=attachment)  
        #             # filename是显示附件名字  
        #             mime.add_header('Content-Disposition', 'attachment', filename=attachment)  
        #             # 获取附件内容  
        #             mime.set_payload(f.read())  
        #             # encoders.encode_base64(mime)  
        #             # 作为附件添加到邮件  
        #             msg.attach(mime)  
        #     self.smtp.sendmail(self.email_from, self.email_to, msg.as_string())
        #     self.smtp.quit()  
        # except smtplib.SMTPException as e:  
        #     print(e)
        if len(self.email_to) > 0:
            to_mail = self.email_to  
            msg['To'] = ','.join(to_mail)
        else:
            raise NoMailListError('还没添加发送人呢，使用add_email_to_list进行填加')

        # mailtype代表邮件类型，纯文本或html等
        msg.attach(MIMEText(body, mailtype))  

        # 有附件内容，才添加到邮件
        if attachment:
            # 二进制方式模式文件  
            with open(attachment, 'rb') as f:  
                # MIMEBase表示附件的对象  
                mime = MIMEBase('text', 'txt', filename=attachment)  
                # filename是显示附件名字  
                mime.add_header('Content-Disposition', 'attachment', filename=attachment)  
                # 获取附件内容  
                mime.set_payload(f.read())  
                # encoders.encode_base64(mime)  
                # 作为附件添加到邮件  
                msg.attach(mime)  
        self.smtp.sendmail(self.email_from, self.email_to, msg.as_string())
        self.smtp.quit()  


def main():
    l = LogRegCon()
    l_return = l.log_control()
    
    if len(l_return) > 0:
        admin = MemoAdmin(l_return)
        admin.logical_control(admin)

if __name__ == "__main__":
    main()

