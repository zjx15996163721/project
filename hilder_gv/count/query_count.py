from flask import Flask
from flask import request
from flask import render_template
from pymongo import MongoClient
from backup import city_dict

app = Flask(__name__)
client = MongoClient('192.168.0.235', 27017)
db = client['gv']

@app.route("/query_all")
def query_all():
    print('开始查询')
    comm_collection = db['community_2018_3_29']
    build_collection = db['building_2018_3_29']
    house_collection = db['house_2018_3_29']
    all_info = {}
    sort_num = []
    co_index_list = city_dict.city_index.values()

    for num in co_index_list:
        sort_num.append(int(num))

    sort_num.sort()
    for value in sort_num:
        # print(value)
        info_dict = {}
        city_count = comm_collection.find({'co_index': int(value)}).count()
        bu_count = build_collection.find({'co_index': int(value)}).count()
        house_count = house_collection.find({'co_index': int(value)}).count()
        info_dict["城市"] = city_dict.dict_city[str(value)]
        info_dict["小区"] = str(city_count)
        info_dict["楼栋"] = str(bu_count)
        info_dict["房号"] = str(house_count)
        print(value,info_dict)
        all_info[str(value)] = info_dict
    # all_info =  str(all_info).replace("},","},\r\n")
    # return render_template('query_all.html', count_dict=all_info)
    return str(all_info)


@app.route("/", methods=['POST', 'GET'])
def query():

    comm_collection = db['community_2018_3_29']
    build_collection = db['building_2018_3_29']
    house_collection = db['house_2018_3_29']

    if request.method == 'GET':
        return render_template('hello.html',)
    city = request.form['city']
    print(city)
    co_index = city_dict.city_index[city]
    print(co_index)

    city_count = comm_collection.find({'co_index': int(co_index)}).count()
    bu_count = build_collection.find({'co_index': int(co_index)}).count()
    house_count = house_collection.find({'co_index': int(co_index)}).count()
    city = city_dict.dict_city[co_index]
    print('城市:' + city + ', 小区:' + str(city_count) + ', 楼栋:' + str(bu_count) + ', 房号:' + str(house_count))
    count_dict = {
        '城市': city,
        '小区': str(city_count),
        '楼栋': str(bu_count),
        '房号': str(house_count),
    }

    return render_template('hello.html', count_dict=count_dict)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081)
