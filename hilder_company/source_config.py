from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import yaml
from lib.log import LogHandler
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, MetaData

log = LogHandler(__name__)

Base = declarative_base()
metadata = MetaData()


class Category(Base):
    __tablename__ = 'category_company'

    id = Column(Integer, primary_key=True)
    name = Column(String(2000))
    request_parameter = Column(String(2000))
    source = Column(String(2000))


class DevelopmentStage(Base):
    __tablename__ = 'development_stage'

    id = Column(Integer, primary_key=True)
    name = Column(String(2000))
    request_parameter = Column(String(2000))


class City(Base):
    __tablename__ = 'city_company'

    id = Column(Integer, primary_key=True)
    name = Column(String(2000))
    request_parameter = Column(String(2000))
    source = Column(String(2000))
    url = Column(String(2000))


class Region(Base):
    __tablename__ = 'region_company'

    id = Column(Integer, primary_key=True)
    name = Column(String(2000))
    request_parameter = Column(String(2000))
    source = Column(String(2000))
    city_id = Column(Integer)


class Block(Base):
    __tablename__ = 'block'

    id = Column(Integer, primary_key=True)
    name = Column(String(2000))
    request_parameter = Column(String(2000))
    source = Column(String(2000))
    region_id = Column(Integer)


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


def get_sqlalchemy_engine():
    """
    获取一个sqlalchemy engine
    :return: Object
    """
    c = yaml.load(open('config.yaml'))['source_config']
    engine = create_engine(
        'mysql+pymysql://{0}:{1}@{2}:{3}'.format(c['user_name'],
                                                 c['password'],
                                                 c['host'],
                                                 c['port'], ))
    engine.execute("CREATE DATABASE IF NOT EXISTS {0} default character set utf8".format(c['db_name']))
    engine.execute("USE {0}".format(c['db_name']))
    return engine


if __name__ == '__main__':
    Base.metadata.create_all(get_sqlalchemy_engine())
