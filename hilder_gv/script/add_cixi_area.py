from pymongo import MongoClient


class Add_area:
    """
    慈溪添加街道信息
    """

    def __init__(self):
        self.area_list = [
            "宗汉镇", "浒山镇", "浒山街道", "宗汉街道", "横河镇", "坎墩镇", "坎墩街道", "庵东镇", "周巷镇", "掌起镇", "观海卫镇", "观城镇", "逍林镇", "新浦镇", "天元镇",
            "鸣鹤镇", "白沙乡", "师桥镇", "范市镇", "长河镇", "崇寿镇", "桥头镇", "胜山镇", "龙山镇", "三北镇", "匡堰镇", "附海镇", "杭州湾镇", "杭州湾新区",
            "慈溪经济开发区", "白沙路街道", "古塘街道",
        ]

    def update_all_building(self):
        client = MongoClient('192.168.0.235', 27017)
        db = client['gv']
        collection = db['community_2018_3_26']

        for i in collection.find({'co_index': 8}):
            print(i)
            for k in self.area_list:
                if k in i['co_address']:
                    i['area'] = k
                    collection.update({'_id': i['_id']}, {'$set': i})
                else:
                    continue
