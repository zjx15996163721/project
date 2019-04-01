import warnings
from pymongo import MongoClient


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Mongo(metaclass=Singleton):

    def __init__(self, host, port=27017, db_name=None, collection_name=None, user_name=None, password=None):
        """
        :param host:
        :param port:
        :param db_name:
        :param collection_name:
        """
        self.host = host
        self.port = int(port)
        self.db = db_name
        self.collection_name = collection_name
        if user_name:
            self.connect = MongoClient(host, port)
            db_auth = self.connect.admin
            db_auth.authenticate(user_name, password)
        else:
            self.connect = MongoClient(host, port)

    def get_collection_object(self):
        warnings.warn('这个方法我早晚给它删了的,你们都别用,请直接调用connect类属性',
                      DeprecationWarning, stacklevel=2)
        client = MongoClient(self.host, self.port)
        db = client[self.db]
        collection = db[self.collection_name]
        return collection

    def get_connection(self):
        warnings.warn('这个方法我早晚给它删了的,这个虽然是单例，你们都别用,请直接调用connect类属性',
                      DeprecationWarning, stacklevel=2)
        return self.connect


if __name__ == '__main__':
    m = Mongo(host='114.80.150.196', port=27777, user_name='fangjia', password='fangjia123456')
    collection_ = m.connect['auction']['auction_new']
    print(collection_.find_one())