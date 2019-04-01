from pymongo import MongoClient


class Add_area:
    """
    东莞添加街道信息
    """

    def __init__(self):
        self.area_list = ['东莞市莞城区',
                          '东莞市东城区',
                          '东莞市万江区',
                          '东莞市南城区',
                          '东莞市石龙镇',
                          '东莞市虎门镇',
                          '东莞市中堂镇',
                          '东莞市望牛墩镇',
                          '东莞市麻涌镇',
                          '东莞市石碣镇',
                          '东莞市高埗镇',
                          '东莞市道滘镇',
                          '东莞市洪梅镇',
                          '东莞市长安镇',
                          '东莞市沙田镇',
                          '东莞市厚街镇',
                          '东莞市松山湖',
                          '东莞市寮步镇',
                          '东莞市大岭山镇',
                          '东莞市大朗镇',
                          '东莞市黄江镇',
                          '东莞市樟木头镇',
                          '东莞市凤岗镇',
                          '东莞市塘厦镇',
                          '东莞市谢岗镇',
                          '东莞市清溪镇',
                          '东莞市常平镇',
                          '东莞市桥头镇',
                          '东莞市横沥镇',
                          '东莞市东坑镇',
                          '东莞市企石镇',
                          '东莞市石排镇',
                          '东莞市茶山镇',
                          '东莞市虎门港',
                          '东莞市生态产业园',
                          ]

    def update_all_building(self):
        client = MongoClient('192.168.0.235', 27017)
        db = client['gv']
        collection = db['building_2018_3_26']

        for i in collection.find({'co_index': 9}):
            print(i)

            for k in self.area_list:
                if k in i['bu_address']:
                    i['area'] = k
                    collection.update({'_id': i['_id']}, {'$set': i})
                else:
                    continue


if __name__ == '__main__':
    a = Add_area()
    a.update_all_building()
