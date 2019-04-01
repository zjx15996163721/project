from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import yaml
from sqlalchemy.orm import sessionmaker, scoped_session

c = yaml.load(open('database_config.yaml'))['mysql_config']
engine = create_engine(
    'mysql+pymysql://{0}:{1}@{2}:{3}'.format(c['user_name'],
                                             c['password'],
                                             c['host'],
                                             c['port']))
engine.execute("USE {0}".format(c['db_name']))
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
