from pymongo import MongoClient
import re


class Add_area:
    """
    解析宁波info
    """

    def update_all_building(self):
        client = MongoClient('192.168.0.235', 27017)
        db = client['gv']
        collection = db['house']

        for i in collection.find({'co_index': 33}):
            info = i['info']
            i['ho_num'] = re.search('房号：(.*?)&', info).group(1)
            i['ho_build_size'] = re.search('建筑面积：(.*?)&', info).group(1)
            i['ho_share_size'] = re.search('分摊面积：(.*?)&', info).group(1)
            i['ho_type'] = re.search('房屋用途：(.*?)"', info).group(1)
            collection.update({'_id': i['_id']}, {'$set': i})


if __name__ == '__main__':
    a = Add_area()
    a.update_all_building()
