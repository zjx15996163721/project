from pymongo import MongoClient


def delete(co_index_list):
    for i in co_index_list:
        collection_bu = db['building']
        collection_bu.delete_many({'co_index': i})

        collection_co = db['community']
        collection_co.delete_many({'co_index': i})

        collection_ho = db['house']
        collection_ho.delete_many({'co_index': i})


if __name__ == '__main__':
    client = MongoClient('192.168.0.235', 27017)
    db = client['gv']

    index_list = [8]
    delete(index_list)
