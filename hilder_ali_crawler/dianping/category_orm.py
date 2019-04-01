from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import yaml
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, MetaData

# 创建对象的基类
Base = declarative_base()
metadata = MetaData()


# 一级分类
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    count = Column(Integer)
    categoryId = Column(String(2000))
    name = Column(String(2000))
    request_parameter = Column(String(2000))
    source = Column(String(2000))
    cityId = Column(String(2000))
    parentId = Column(Integer)


# 二级分类
class SecondCategory(Base):
    __tablename__ = 'second_category'

    id = Column(Integer, primary_key=True)
    count = Column(Integer)
    second_categoryId = Column(String(2000), index=True)
    name = Column(String(2000))
    cityId = Column(String(2000), index=True)
    parentId = Column(Integer)


# 三级分类
class ThirdCategory(Base):
    __tablename__ = 'third_category'

    id = Column(Integer, primary_key=True)
    count = Column(Integer)
    third_categoryId = Column(String(2000))
    name = Column(String(2000))
    cityId = Column(String(2000))
    parentId = Column(Integer)


# 城市
class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    city_id = Column(String(2000))
    name = Column(String(2000))
    pingyin_name = Column(String(2000))


# 区域
class Region(Base):
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    region_id = Column(String(2000), index=True)
    name = Column(String(2000))
    pingyin_name = Column(String(2000))
    city_id = Column(Integer)


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
    db_session = scoped_session(sessionmaker(autocommit=autocommit,
                                             autoflush=autoflush,
                                             bind=engine))
    return db_session


# 初始化数据库连接
def get_sqlalchemy_engine():
    """
    获取一个sqlalchemy engine
    :return: Object
    """
    c = yaml.load(open('config_dianping.yaml'))['mysql_config']
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
