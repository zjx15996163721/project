from pymongo import MongoClient
import redis
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection = m['fangjiaguanjia']['price']

r = redis.Redis(host='localhost', port='6379')


def run():
    count = 0
    for i in collection.find(no_cursor_timeout=True):
        count += 1
        print(count)
        haCode = i['haCode']
        flag = r.sadd('guanjia', haCode)
        if flag == 1:
            # 不重复的数据
            print(i)
        elif flag == 0:
            # 重复的数据
            collection.delete_one({'haCode': haCode})
            print('删除一条数据 haCode={}'.format(haCode))


if __name__ == '__main__':
    run()


