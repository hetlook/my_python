# toutiao_sql.py
# 完成与对mysql数据库数据的操作，完成数据的发布

import re
import redis
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, TIME, log
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_
from sqlalchemy import or_
from datetime import datetime

Base = declarative_base()


class Authors(Base):
    __tablename__ = 'authors'

    id = Column('author_id', Integer, primary_key=True)
    name = Column('name', String(50), unique=True)
    city = Column('city', String(20))

    def __repr__(self):
        return self.name

class Articles(Base):
    __tablename__ = 'articles'

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(20))
    content = Column('content', String(180))
    comment = Column('comment', String(180))
    eate_date = Column('eate_date', TIME())

    author_id = Column(Integer, ForeignKey('authors.author_id'))
    authors = relationship('Authors', back_populates="articles")

    def __repr__(self):
        temp = [self.title, self.content]
        return str(temp)

# 一对多的关联
Authors.articles = relationship('Articles', back_populates='authors', order_by=Articles.id)

# mysql+pymysql://username:password@host/db
# engine = create_engine('mysql+pymysql://root:king123@localhost/toutiaoplus?charset=utf8', echo=True)
# Base.metadata.create_all(bind=engine)


class DataManage:
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://root:king123@localhost/toutiaoplus?charset=utf8', echo=True)
        # session
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()

    def show_all_article_title(self):
        """展示所有article"""
        article_list = self.session.query(Articles).all()
        title_list = []
        for x in article_list:
            title_list.append(x.title)
        # print(title_list)
        return title_list

    def query_article_by_title(self, title):
        """根据title查询文章"""
        result = self.session.query(Articles).filter(Articles.title == title).one()
        # print(result.content)
        return result.content

    def add_article(self, title, content, name):
        """根据（文章名、内容、作者）添加文章"""
        name_list = self.query_author()
        if name in name_list:
            arti = Articles()
            arti.title = title
            arti.content = content
            arti.author_id = self.session.query(Authors).filter(Authors.name == name).one().id
            arti.eate_date = f'{datetime.now():%Y-%m-%d %H:%M}'
            self.session.add(arti)
            self.session.commit()
            print('添加成功')
        else:
            print("作者不存在")
            self.add_author()

    def delete_article(self, id):
        """根据文章id删除文章"""
        self.session.query(Articles).filter(Articles.id == id).delete()
        self.session.commit()
        print("删除成功！")

    def add_author(self):
        """添加作者信息"""
        auth = Authors()
        auth.name = input("author name:") 
        auth.city = input("author city:")
        print("开始添加作者。。。。。")
        self.session.add(auth)
        self.session.commit()
        print("作者添加完成。。。。。")

    def query_author(self):
        """查询所有作者姓名"""
        author_list = self.session.query(Authors).all()
        result_list = []
        for x in author_list:
            result_list.append(str(x))
        # print(result_list)
        return(result_list)

    def publish_article(self, channel, title):
        """发布文章"""
        content = self.query_article_by_title(title)
        print(content)
        client = redis.Redis()
        client.publish(channel, content)

def main():
    menu = """
        操作选项:
        [1]:显示所有文章title
        [2]:添加文章
        [3]:发布文章
        [q]:退出
    """
    try:
        dm = DataManage()
        while True:
            print(menu)
            operation = input("请输入需要进行的操作:")
            if operation == 'q':
                print('退出')
                break
            elif operation == '1':
                title = dm.show_all_article_title()
                print(title)
            elif operation == '2':
                title = input('请输入文章名：')
                content = input('请输入内容：')
                name = input('请输入作者：')
                dm.add_article(title, content, name)
            elif operation == '3':
                title = input("请输入需要发布的文章title：")
                channels = dm.query_author()
                print("channels:", channels)
                channel = input("请输入channel：")
                if channel in channels:
                    dm.publish_article(channel, title)
                else:
                    print("channel不存在")
            else:
                print("没有需要的操作！")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()