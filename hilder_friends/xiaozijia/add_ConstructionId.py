from lib.log import LogHandler
from lib.mongo import Mongo

log = LogHandler(__name__)

m = Mongo(host='114.80.150.196', port=27777, user_name='goojia', password='goojia7102')
xiaozijia_price_1 = m.connect['fangjia_crawl']['xiaozijia_price_1']
xiaozijia_comm = m.connect['friends']['xiaozijia_comm']


def update():
    for i in xiaozijia_price_1.find(no_cursor_timeout=True):
        _id = i['_id']
        data = xiaozijia_comm.find_one({'ConstructionPhaseId': _id})
        ConstructionId = data['ConstructionId']
        xiaozijia_price_1.find_one_and_update({'_id': _id}, {'$set': {'ConstructionId': ConstructionId}})
        print('更新一条数据 ConstructionId={}'.format(ConstructionId))


if __name__ == '__main__':
    update()