from lib.mongo import Mongo

m = Mongo('192.168.0.235', 27017)
coll = m.connect['amap']['poi_new_2018_4']
coll_food = m.connect['amap']['food_poi']

type_code_list = ["050000", "050100", "050101", "050102", "050103", "050104", "050105", "050106", "050107", "050108",
                  "050109", "050110", "050111", "050112", "050113", "050114", "050115", "050116", "050117", "050118",
                  "050119", "050120", "050121", "050122", "050123", "050200", "050201", "050202", "050203", "050204",
                  "050205", "050206", "050207", "050208", "050209", "050210", "050211", "050212", "050213", "050214",
                  "050215", "050216", "050217", "050300", "050301", "050302", "050303", "050304", "050305", "050306",
                  "050307", "050308", "050309", "050310", "050311", "050400", "050500", "050501", "050502", "050503",
                  "050504", "050600", "050700", "050800", "050900"]

for i in coll.find():
    if i['typecode'] in type_code_list:
        # del i['_id']
        coll_food.insert_one(i)
        print(i)