# admin.py

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, TIME
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
    city = Column('city', String(20), unique=True)

    def __repr__(self):
        temp = f'{self.id}-{self.name}-{self.city}'
        return temp

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
        temp = f'{self.id}-{self.title}-{self.content}-{self.comment}-{self.eate_date}'
        return temp

# 一对多的关联
Authors.articles = relationship('Articles', back_populates='authors', order_by=Articles.id)


class DataManage:
    def __init__(self):
        # mysql+pymysql://username:password@host/db
        self.engine = create_engine('mysql+pymysql://root:king123@localhost/de8ug?charset=utf8', echo=True)
        # session
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()

    def show_data(self):
        """展示所有数据"""
        temp = self.session.query(Authors, Articles).filter(Articles.author_id == Authors.id).all()
        print(temp)

    def query_article_id(self, id):
        """根据id查询文章"""
        temp = self.session.query(Articles).filter(Articles.id == id).all()
        print(temp)
        return {"result":temp}


    def query_article_all(self):
        """展示所有article"""
        temp = self.session.query(Articles).all()
        print(temp)
        return {"result":temp}

    def add_article(self, title, content, name):
        """根据（文章名、内容、作者）添加文章"""
        arti = Articles()
        arti.title = title
        arti.content = content
        arti.author_id = self.session.query(Authors).filter(Authors.name == name).one().id
        # arti.eate_date = '{dt:%Y-%m-%d %H:%M}'.format(dt=datetime.now())
        arti.eate_date = f'{datetime.now():%Y-%m-%d %H:%M}'
        self.session.add(arti)
        self.session.commit()
        print('添加成功')

    def delete_article(self, id):
        """根据文章id删除文章"""
        self.session.query(Articles).filter(Articles.id == id).delete()
        self.session.commit()
        print("删除成功！")
    def add_author(self, id, name, city):
        """添加作者信息"""
        auth = Authors()
        auth.author_id = id
        auth.name = name 
        auth.city = city
        self.session.add(auth)
        self.session.commit()


def main():
    menu = """
        操作选项
        ---show ,展示所有数据
        ---add,添加文章
        ---delete, 根据文章id删除文章
    """
    try:
        dm = DataManage()
        print(menu)
        operation = input("请输入需要进行的操作")
        if operation == 'show':
            dm.query_article_all()
        elif operation == 'add':
            title = input('请输入文章名：')
            content = input('请输入内容：')
            name = input('请输入作者：')
            dm.add_article(title, content, name)
        elif operation == 'delete':
            id = input("请输入需要删除的文章id：")
            dm.delete_article(id)
        else:
            print("没有需要的操作！")

    except Exception as e:
        print(e)



if __name__ == "__main__":
    main()