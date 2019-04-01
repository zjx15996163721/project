"""
小资家手机app用fiddler抓包,抓取均价
"""
import requests
from pymongo import MongoClient
import pymongo
from urllib import parse
from lib.log import LogHandler
from lib.proxy_iterator import Proxies
p = Proxies()
p = p.get_one(proxies_number=7)
# proxies = {'https': 'http://FANGJIAHTT1:HGhyd7BF@http-proxy-sg2.dobel.cn:9180',
#            'http': 'http://FANGJIAHTT1:HGhyd7BF@http-proxy-sg2.dobel.cn:9180'}
log = LogHandler(__name__)
m = MongoClient(host='114.80.150.196', port=27777, username='goojia', password='goojia7102')
collection_comm = m['friends']['xiaozijia_comm']
collection_user = m['friends']['xiaozijia_user']


class UnitPrice:
    def __init__(self, proxies):
        self.Authorization_list = []
        self.proxies = proxies

    def get_authorization(self):
        total_count = 0
        for user in collection_user.find({'phone_status': 0}, no_cursor_timeout=True):
            total_count += 1
            print(total_count)
            start_url = 'http://www.xiaozijia.cn:8002/Token'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Proxy-Connection': 'keep-alive',
                'Accept': '*/*',
                'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, ja-JP;q=0.8, ko-KR;q=0.7, zh-Hant-CN;q=0.6',
                'Accept-Encoding': 'gzip, deflate',
                'User-Agent': 'xiao zi jiaiOS/1.2.1 (iPhone; iOS 11.4.1; Scale/2.00)',
                'Host': 'www.xiaozijia.cn:8002'
            }
            data = {
                'Password': user['password'],
                'grant_type': 'password',
                'username': user['username'],
            }
            try:
                r = requests.post(url=start_url, data=data, headers=headers, proxies=self.proxies)
                # print(r.cookies)
                # cookie = '.AspNet.Cookies=' + re.search('\.AspNet\.Cookies=(.*?) ', str(r.cookies), re.S | re.M).group(1)
                # print(cookie)
                print(r.status_code)
                # if r.status_code != 200:
                #     collection_user.find_one_and_update({'username': user['username']}, {'$set': {'phone_status': 1}})
                #     print('账户失效 username={}, password={}'.format(user['username'], user['password']))

                access_token = r.json()['access_token']
                token_type = r.json()['token_type']
                authorization = token_type + ' ' + access_token
                print(authorization)
            except Exception as e:
                log.error(e)
                continue
            # 判断剩余评估次数
            count_url = 'http://www.xiaozijia.cn:8002/api/Account/GetAssets'
            count_headers = {
                'User-Agent': 'xiao zi jiaiOS/1.2.1 (iPhone; iOS 11.4.1; Scale/2.00)',
                'Host': 'www.xiaozijia.cn:8002',
                'Connection': 'keep-alive',
                'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, ja-JP;q=0.8, ko-KR;q=0.7, zh-Hant-CN;q=0.6',
                'Accept-Encoding': 'gzip, deflate',
                'Authorization': authorization
            }
            try:
                res = requests.get(url=count_url, headers=count_headers, proxies=self.proxies)
                print(res.text)
                count = res.json()['QueryCount']
            except Exception as e:
                log.error(e)
                continue
            print('已评估{}次'.format(count))
            if int(count) == 3:
                print('评估次数用完')
            elif int(count) == 2:
                self.Authorization_list.append(authorization)
            elif int(count) == 1:
                self.Authorization_list.append(authorization)
                self.Authorization_list.append(authorization)
            elif int(count) == 0:
                self.Authorization_list.append(authorization)
                self.Authorization_list.append(authorization)
                self.Authorization_list.append(authorization)
        self.get_unit_price()

    def get_unit_price(self):
        # 无锡：3202  合肥：3401  上海：3101  漳州：3506
        # 上海：自动估价 模型估价 案例较少
        # 无锡：自动估价 案例较少
        # 合肥: 自动估价 案例较少
        # 漳州:
        Authorization_iter = iter(self.Authorization_list)
        for i in collection_comm.find({"CityGBCode": {'$in': ['3202', '3401', '3101']}}, no_cursor_timeout=True):
            if 'ResultMessage' in i:
                if i['ResultMessage'] in ['自动估价', '模型估价', '案例较少']:
                    if 'unit_price_2018_12' not in i:
                        ConstructionName = i['ConstructionName']
                        print(ConstructionName)
                        parse_ConstructionName = parse.quote(ConstructionName)
                        construction_url = 'http://www.xiaozijia.cn:8002/api/v1/BaseData/SearchContrution/' + i['CityGBCode'] + '/' + parse_ConstructionName
                        try:
                            authorization = next(Authorization_iter)
                        except StopIteration as e:
                            log.error(e)
                            break
                        headers = {
                            'Connection': 'keep-alive',
                            'Host': 'www.xiaozijia.cn:8002',
                            'User-Agent': 'xiao zi jiaiOS/1.2.1 (iPhone; iOS 11.4.1; Scale/2.00)',
                            'Authorization': authorization,
                            # 'Cookie': cookie
                        }
                        try:
                            r = requests.get(url=construction_url, headers=headers, proxies=self.proxies)
                            print(r.text)
                            construction_data = r.json()[0]
                        except Exception as e:
                            log.error(e)
                            # self.Authorization_list.append(authorization)
                            continue
                        CID = construction_data['Id']
                        Address = construction_data['Address']
                        City = i['CityGBCode'] + '00'
                        DivisionId_url = 'http://www.xiaozijia.cn:8002/api/v1/BaseData/ConstructionInfo/' + str(CID)
                        try:
                            res = requests.get(url=DivisionId_url, headers=headers, proxies=self.proxies)
                        except Exception as e:
                            log.error(e)
                            # self.Authorization_list.append(authorization)
                            continue
                        try:
                            AreaId = res.json()['DivisionId']
                            ConstructionPhaseId = res.json()['ConstructionPhaseId']
                        except Exception as e:
                            log.error(e)
                            # self.Authorization_list.append(authorization)
                            continue
                        building_url = 'http://www.xiaozijia.cn:8002/api/v1/BaseData/House/' + str(ConstructionPhaseId) + '/0'
                        try:
                            response = requests.get(url=building_url, headers=headers, proxies=self.proxies)
                            print(response.text)
                            building_data = response.json()[0]
                        except Exception as e:
                            log.error('没有数据 e={}'.format(e))
                            self.Authorization_list.append(authorization)
                            continue
                        BID = building_data['Id']
                        IdSub = building_data['IdSub']
                        house_url = 'http://www.xiaozijia.cn:8002/api/v1/BaseData/House/' + str(IdSub) + '/1'
                        try:
                            res_house = requests.get(url=house_url, headers=headers, proxies=self.proxies)
                            house_data = res_house.json()[0]
                        except Exception as e:
                            log.error(e)
                            # self.Authorization_list.append(authorization)
                            continue
                        HId = house_data['Id']
                        price_url = 'http://www.xiaozijia.cn:8002/api/v1/Order/GetQueryPrice'
                        data = {
                            'Address': Address,
                            'AreaId': str(AreaId),
                            'BId': str(BID),
                            'BuildArea': '100',
                            'CId': str(CID),
                            'City': str(City),
                            'HId': str(HId)
                        }
                        try:
                            res_price = requests.post(url=price_url, data=data, headers=headers, proxies=self.proxies)
                        except Exception as e:
                            log.error(e)
                            # self.Authorization_list.append(authorization)
                            continue
                        print(res_price.text)
                        print(res.status_code)
                        if res_price.status_code == 200:
                            if 'ResultMessage' in res_price.json():
                                collection_comm.update_one({'ConstructionId': i['ConstructionId']},
                                                           {'$set': {'ResultMessage': res_price.json()['ResultMessage'],
                                                                     'info_2018_12': res_price.text,
                                                                     'unit_price_2018_12': int(res_price.json()['UnitPrice'])}})
                                log.info('更新均价{}和ResultMessage{}'.format(int(res_price.json()['UnitPrice']), res_price.json()['ResultMessage']))
                                if '不' in res_price.json()['ResultMessage']:
                                    self.Authorization_list.append(authorization)

                        elif '网络不可用' or '账号登录异常' in res_price.text:
                            # self.Authorization_list.append(authorization)
                            log.error('账户失效')
                        else:
                            log.info('请求失败')


if __name__ == '__main__':

    price = UnitPrice(p)
    price.get_authorization()



