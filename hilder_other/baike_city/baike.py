import requests
import urllib
import re
from baike_city.city_name import city_list
from lib.mongo import Mongo
from datetime import datetime
import yaml
from lib.log import LogHandler
from lib.standardization import standard_city

setting = yaml.load(open('config.yaml'))
log = LogHandler('baidubaike')
connect = Mongo(setting['baidubaike']['mongo']['host']).connect
coll = connect[setting['baidubaike']['mongo']['db']][setting['baidubaike']['mongo']['collection']]

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'BAIDUID=98C2249E28948F3E040B59450E9F1ED2:FG=1; BIDUPSID=98C2249E28948F3E040B59450E9F1ED2; PSTM=1514361799; Hm_lvt_55b574651fcae74b0a9f1cf9c8d7c93a=1523269340; Hm_lpvt_55b574651fcae74b0a9f1cf9c8d7c93a=1523269340; pgv_pvi=1332027392; pgv_si=s3426598912',
    'Host': 'baike.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
}


def crawler_baike():
    for city in city_list:
        print(city)
        i = urllib.parse.quote(city)
        url = 'https://baike.baidu.com/item/' + i
        res = requests.get(url=url, headers=headers)
        html = res.content.decode('UTF-8', 'ignore')

        # 中文名称
        try:
            chinese_name = re.search(r'中文名称</dt>(.*?)<dd(.*?)>(.*?)</dd>', html, re.S | re.M).group(3).strip()
            chinese_name = re.sub('<[^>]+>', '', chinese_name).strip()
        except Exception as e:
            chinese_name = None

        # 外文名称
        try:
            foreign_names = re.search(r'外文名称</dt>(.*?)<dd(.*?)>(.*?)</dd>', html, re.S | re.M).group(3).strip()
            foreign_names = re.sub('<[^>]+>', '', foreign_names).strip()
        except Exception as e:
            foreign_names = None

        # 别名
        try:
            alias = re.search(r'别&nbsp;&nbsp;&nbsp;&nbsp;名</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(
                1).strip()
            alias = re.sub('<[^>]+>', '', alias).strip()
        except Exception as e:
            alias = None

        # 行政区划(Administrative_categories)
        try:
            administrative_division = re.search(r'行政区类别</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            administrative_division = re.sub('<[^>]+>', '', administrative_division).strip()
        except Exception as e:
            administrative_division = None

        # 所属地区(Attribution_area)
        try:
            affiliating_area = re.search(r'所属地区</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            affiliating_area = re.sub('<[^>]+>', '', affiliating_area).strip()
        except Exception as e:
            affiliating_area = None

        # 下辖地区(governs_area)
        try:
            governs_area = re.search(r'下辖地区</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            governs_area = re.sub('<[^>]+>', '', governs_area).strip()
        except Exception as e:
            governs_area = None

        # 政府驻地
        try:
            government_resident = re.search(r'政府驻地</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            government_resident = re.sub('<[^>]+>', '', government_resident).strip()
        except Exception as e:
            government_resident = None

        # 电话区号(Telephone_code)
        try:
            area_code = re.search(r'电话区号</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            area_code = re.sub('<[^>]+>', '', area_code).strip()
        except Exception as e:
            area_code = None

        # 邮政区码
        try:
            zip_code = re.search(r'邮政区码</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            zip_code = re.sub('<[^>]+>', '', zip_code).strip()
        except Exception as e:
            zip_code = None

        # 地理位置(geographical_position)
        try:
            geographic_position = re.search(r'地理位置</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            geographic_position = re.sub('<[^>]+>', '', geographic_position).strip()
        except Exception as e:
            geographic_position = None

        # 面积
        try:
            area = re.search(r'面&nbsp;&nbsp;&nbsp;&nbsp;积</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            area = re.sub('<[^>]+>', '', area).strip()
        except Exception as e:
            area = None

        # 人口
        try:
            population = re.search(r'人&nbsp;&nbsp;&nbsp;&nbsp;口</dt>.*?<dd.*?>(.*?)<', html, re.S | re.M).group(
                1).strip()
            population = re.sub('<[^>]+>', '', population).strip()
        except Exception as e:
            population = None

        # 方言
        try:
            localism = re.search(r'方&nbsp;&nbsp;&nbsp;&nbsp;言</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(
                1).strip()
            localism = re.sub('<[^>]+>', '', localism).strip()
        except Exception as e:
            localism = None

        # 气候条件(Climatic_conditions)
        try:
            weather_conditions = re.search(r'气候条件</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            weather_conditions = re.sub('<[^>]+>', '', weather_conditions).strip()
        except Exception as e:
            weather_conditions = None

        # 著名景点
        try:
            famous_scenery = re.search(r'著名景点</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            famous_scenery = re.sub('<[^>]+>', '', famous_scenery).strip()
        except Exception as e:
            famous_scenery = None

        # 机场
        try:
            airport = re.search(r'机&nbsp;&nbsp;&nbsp;&nbsp;场</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(
                1).strip()
            airport = re.sub('<[^>]+>', '', airport).strip()
        except Exception as e:
            airport = None

        # 火车站
        try:
            railway_station = re.search(r'火车站</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            railway_station = re.sub('<[^>]+>', '', railway_station).strip()
        except Exception as e:
            railway_station = None

        # 车牌代码
        try:
            license_code = re.search(r'车牌代码</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            license_code = re.sub('<[^>]+>', '', license_code).strip()
        except Exception as e:
            license_code = None

        # 地区生产总值（Gross regional product）
        try:
            GRP = re.search(r'地区生产总值</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            GRP = re.sub('<[^>]+>', '', GRP).strip()
        except Exception as e:
            GRP = None
        # 人均生产总值
        try:
            GNPP = re.search(r'人均生产总值</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            GNPP = re.sub('<[^>]+>', '', GNPP).strip()
        except Exception as e:
            GNPP = None
        # 人均支配收入（Per capita income）
        try:
            per_capita_income = re.search(r'人均支配收入</dt>.*?<dd.*?>(.*?)</dd', html, re.S | re.M).group(1).strip()
            per_capita_income = re.sub('<[^>]+>', '', per_capita_income).strip()
        except Exception as e:
            per_capita_income = None
        # 消费品零售额
        try:
            retail_sales_of_consumer_goods = re.search(r'消费品零售额</dt>.*?<dd.*?>(.*?)<sup', html, re.S | re.M).group(
                1).strip()
            retail_sales_of_consumer_goods = re.sub('<[^>]+>', '', retail_sales_of_consumer_goods).strip()
        except Exception as e:
            retail_sales_of_consumer_goods = None

        # 住户存款总额
        try:
            total_household_deposits = re.search(r'住户存款总额</dt>.*?<dd.*?>(.*?)<sup', html, re.S | re.M).group(1).strip()
            total_household_deposits = re.sub('<[^>]+>', '', total_household_deposits).strip()
        except Exception as e:
            total_household_deposits = None
        # 市树市花
        try:
            were_flower = re.search(r'市树市花</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            were_flower = re.sub('<[^>]+>', '', were_flower).strip()
        except Exception as e:
            were_flower = None
        # 著名高校
        try:
            famous_universities = re.search(r'著名高校</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'学&nbsp;&nbsp;&nbsp;&nbsp;校</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'高等院校</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'重点高校</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'高等学府</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'著名学府</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'高&nbsp;&nbsp;&nbsp;&nbsp;校</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'主要高校</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'大&nbsp;&nbsp;&nbsp;&nbsp;学</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            if not famous_universities:
                famous_universities = re.search(r'知名高校</dt>.*?<dd.*?>(.*?)</dd>', html,
                                                re.S | re.M)
            famous_universities = famous_universities.group(1).strip()
            famous_universities = re.sub('<[^>]+>', '', famous_universities).strip()
        except Exception as e:
            famous_universities = None

        # 市长
        try:
            mayor = re.search('市&nbsp;&nbsp;&nbsp;&nbsp;长</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1)
            mayor = re.sub('<[^>]+>', '', mayor).strip()
        except Exception as e:
            mayor = None
        # 行政代码
        try:
            administrative_code = re.search('行政代码</dt.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1)
            administrative_code = re.sub('<[^>]+>', '', administrative_code).strip()
        except Exception as e:
            administrative_code = None
        # 城市精神
        try:
            city_spirit = re.search('城市精神</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            city_spirit = re.sub('<[^>]+>', '', city_spirit).strip()
        except Exception as e:
            city_spirit = None
        # 人类发展指数
        try:
            human_development_index = re.search('人类发展指数</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            human_development_index = re.sub('<[^>]+>', '', human_development_index).strip()
        except Exception as e:
            human_development_index = None
        # 城市简称
        try:
            city_abbreviation = re.search('城市简称</dt>.*?<dd.*?>(.*?)</dd>', html, re.S | re.M).group(1).strip()
            city_abbreviation = re.sub('<[^>]+>', '', city_abbreviation).strip()
        except Exception as e:
            city_abbreviation = None
        is_true, city = standard_city(city)
        if not is_true:
            print(city)
        data = {
            'chinese_name': chinese_name,
            'foreign_names': foreign_names,
            'alias': alias,
            'administrative_division': administrative_division,
            'affiliating_area': affiliating_area,
            'governs_area': governs_area,
            'government_resident': government_resident,
            'area_code': area_code,
            'zip_code': zip_code,
            'geographic_position': geographic_position,
            'area': area,
            'population': population,
            'famous_scenery': famous_scenery,
            'localism': localism,
            'weather_conditions': weather_conditions,
            'airport': airport,
            'railway_station': railway_station,
            'license_code': license_code,
            'GRP': GRP,
            'GNPP': GNPP,
            'per_capita_income': per_capita_income,
            'retail_sales_of_consumer_goods': retail_sales_of_consumer_goods,
            'total_household_deposits': total_household_deposits,
            'were_flower': were_flower,
            'famous_universities': famous_universities,
            'mayor': mayor,
            'administrative_code': administrative_code,
            'city_spirit': city_spirit,
            'human_development_index': human_development_index,
            'city_abbreviation': city_abbreviation,
            'city': city,
            'update_time': datetime.now()
        }
        for i in data:
            try:
                data[i] = data[i].replace('\n', '').replace('&nbsp;', '')
                data[i] = re.sub('\[\d+\]', '', data[i])
            except Exception as e:
                pass
        print(data)
        coll.update_one({'city': city}, {'$set': data}, True)
        # log.info(data)


if __name__ == '__main__':
    crawler_baike()
