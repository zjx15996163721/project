import re
from pymongo import MongoClient
m = MongoClient(host='114.80.150.196',
                    port=27777,
                    username='goojia',
                    password='goojia7102')
house_loudong_collection = m['fangjia']['house_loudong']


def count():
    count = 0
    total_count = 0
    for data in house_loudong_collection.find():
        total_count += 1
        print('到第{}条'.format(total_count))
        if 'status' in data.keys():
            if data['status'] == 0 or data['status'] == 5:
                count += 1
                print('状态为0和5的有{}条'.format(count))


def direction():
    count = 0
    total_count = 0
    for data in house_loudong_collection.find({}):
        total_count += 1
        print('到第{}条'.format(total_count))
        if 'status' in data.keys():
            if data['status'] == 0 or data['status'] == 5:
                if 'direction' in data.keys():
                    direction = data['direction']
                    if direction is not None and direction != 0 and direction != -1:
                        print(direction)
                        count += 1
                        print('状态为0和5的,且有朝向的有{}条'.format(count))
    print('状态为0和5的,且有朝向的有{}条'.format(count))


if __name__ == '__main__':
    # count()
    direction()