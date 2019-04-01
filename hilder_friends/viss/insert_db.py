from pymongo import MongoClient
import datetime

l_m = MongoClient('114.80.150.196', 27777,username='goojia',password='goojia7102')
result_collection = l_m['friends']['viss']
data = {
    "Id": "525ee949-03ce-4eeb-afc7-360b83ba1454",
    "ProjectId": 2522,
    "ProjectName": "潍坊六村",
    "Photos": [{
        "TypeName": "建筑物立面图",
        "Title": "内部道路-潍坊六村.JPG",
        "Url": "http://ueas.surea.com/imgUploads/20139/fe4b443ba1c54663b7055ceaba1d6b11.JPG",
        "T_Url": "http://ueas.surea.com/imgUploads/20139/T_fe4b443ba1c54663b7055ceaba1d6b11.JPG"
    }],
    "ListPhoto": {
        "TypeName": "建筑物立面图",
        "Title": "内部道路-潍坊六村.JPG",
        "Url": "http://ueas.surea.com/imgUploads/20139/fe4b443ba1c54663b7055ceaba1d6b11.JPG",
        "T_Url": "http://ueas.surea.com/imgUploads/20139/T_fe4b443ba1c54663b7055ceaba1d6b11.JPG"
    },
    "LngLat": None,
    "ProjectPrice": 94600,
    "Address": "潍坊六村",
    "CirclePosition": None,
    "District": None,
    "PlateID": 0,
    "Plate": None,
    "CompletionYear": None,
    "ProjectType": None,
    "EastTo": None,
    "SouthTo": None,
    "WestTo": None,
    "NorthTo": None,
    "ProjectLevel": 0,
    "Developer": None,
    "PropertyManagement": None,
    "ConstructionArea": None,
    "LandArea": None,
    "PropertyManagementFee": None,
    "ParkingSpace": None,
    "GreenRate": None,
    "CubicRate": None,
    "Infrastructure": None,
    "SideTraffic": None,
    "SideFacility": None,
    "SideSchool": None,
    "AuditStatus": 4,
    "Status": 0,
    "StatusMemo": None,
    "PriceMemo": None,
    "RecentBasePrices": None,
    "DistrictBasePrices": None,
    "PlateBasePrices": None,
    "isCurrentFavorite": False,
    "Distance": 0,
    "MoM": -0.78,
    "IsVilla": False,
    'crawler_time': datetime.datetime.now()
}
result_collection.insert_one(data)
print("插入一条数据{}".format(data))