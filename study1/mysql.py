#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, MetaData
Base = declarative_base()

engine = create_engine('mysql+pymysql://{0}:{1}@{2}:{3}'.format('root', '123456', 'localhost', '3306'))
# engine.execute("CREATE DATABASE IF NOT EXISTS {0} default character set utf8".format('test'))
engine.execute("USE {0}".format('test'))

DBSession = sessionmaker(bind=engine)


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(String(50))
    address = Column(String(50))


def inquire(class_base, filter_source):
    session = DBSession()
    return session.query(class_base).filter(class_base.name == filter_source).all()


def insert(data_obj, type_class):
    session = DBSession()
    name = data_obj.name
    if not session.query(type_class).filter(type_class.name == name).first():
        session.add(data_obj)
        session.commit()
        session.close()
        print('插入成功')
    else:
        print('数据存在')


def delete(type_class, filter_source):
    session = DBSession()
    session.query(type_class).filter(type_class.name == filter_source).delete(synchronize_session=False)
    session.commit()
    print('删除成功')


Base.metadata.create_all(engine)


if __name__ == '__main__':
    # user = User(name='zjx', age='25', address='abc')
    # insert(user, User)
    #
    # data = inquire(User, 'zjx')
    # print(data[0].name)
    delete(User, 'zjx')



