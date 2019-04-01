import yaml

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, MetaData, Date
from flaskr.models import Base
# Base = declarative_base()
metadata = MetaData()


# db_session
def get_sqlalchemy_session(engine=None, autocommit=False, autoflush=True):
    """
    获取一个sqlalchemy session

    How to use:

        # 获取一个文章列表
        from lib.models.article import Article
        db_session = get_sqlalchemy_session()
        articles = db_session.query(Article).all()
        print(articles)
        db_session.close()

    :return: Object
    """
    if not engine:
        engine = get_sqlalchemy_engine()
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    return db_session


# 初始化数据库连接
def get_sqlalchemy_engine():
    """
    获取一个sqlalchemy engine
    :return: Object
    """
    c = yaml.load(open('database_config.yaml'))['mysql_config']
    engine = create_engine(
        'mysql+pymysql://{0}:{1}@{2}:{3}'.format(c['user_name'],
                                                 c['password'],
                                                 c['host'],
                                                 c['port']))
    # 第一次创建数据库取消注释
    engine.execute("CREATE DATABASE IF NOT EXISTS {0} default character set utf8".format(c['db_name']))
    engine.execute("USE {0}".format(c['db_name']))
    return engine


if __name__ == '__main__':
    Base.metadata.create_all(get_sqlalchemy_engine())
