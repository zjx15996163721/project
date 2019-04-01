"""
url = 'http://hkrealestate.haikou.gov.cn/?page_id=1463'
co_index :14
海口
程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests

co_index = "14"
city = "海口"


class Haikou(Crawler):
    def __init__(self):
        self.s = requests.session()
        self.headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Cookie': 'PHPSESSID=sq4asdaq5bmeqjdrs3n4a71h1h; slimstat_tracking_code=741072.767f13385e08aafb4619510f78034160',
            'Referer': 'http://hkrealestate.haikou.gov.cn/wp_myself/housequery/queryProjectInfo.php',
            'Postman-Token': "c67c04c6-f1e2-44aa-bd0b-d6560456a17b"
        }
        self.start_url = 'http://hkrealestate.haikou.gov.cn/wp_myself/housequery/queryProjectInfo.php'
        self.formdata = {"action": "queryProjectLists", "webUrl": '1'}
        self.url = 'http://hkrealestate.haikou.gov.cn/wp_myself/housequery/projectBuildHouseAction.php'

    def start_crawler(self):
        self.s.get('http://hkrealestate.haikou.gov.cn/')
        url = "http://hkrealestate.haikou.gov.cn/wp_myself/housequery/projectBuildHouseAction.php"
        for i in range(1, 62):
            page = str(i)
            payload = {
                'action': 'queryProjectLists',
                'page': page
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                'Referer': "http://hkrealestate.haikou.gov.cn/wp_myself/housequery/queryProjectInfo.php",
                'Cache-Control': "no-cache",
                'Postman-Token': "c57f57a2-32aa-2739-ff2c-77c7e078bcdc"
            }

            res = self.s.request("POST", url, data=payload, headers=headers)
            k = re.findall("onclick=\"doview\(('\d+','.*?')\)", res.text, re.S | re.M)
            for n in k:
                formdata = {}
                ret = re.split(',', n)
                co_id = formdata["pk"] = ret[0].strip("\\'")
                num = ret[1].strip("'")
                load = {
                    'action': 'querySingleProject',
                    'pk': co_id,
                    'num': num,
                    'page': page,
                    'webUrl': 1,
                }
                try:
                    response = self.s.post(url, data=load, headers=headers)
                except Exception as e:
                    print("co_index={},小区错误".format(co_index),e)

                    continue
                self.get_comm_info(response, co_id)

    def get_comm_info(self, comm_res, co_id):
        comm = Comm(co_index)
        con = comm_res.text
        comm.co_name = re.search('项目名称.*?">(.*?)<', con, re.S | re.M).group(1)
        comm.co_id = co_id
        comm.co_address = re.search('项目地址.*?<td>(.*?)<', con, re.S | re.M).group(1)
        comm.co_develops = re.search('开 发 商：.*?<td.*?>(.*?)<', con, re.S | re.M).group(1)
        comm.co_all_size = re.search('建设用地面积.*?<td>(.*?)</td>', con, re.S | re.M).group(1)
        comm.co_size = re.search('占地面积.*?<td>(.*?)</td>', con, re.S | re.M).group(1)
        comm.co_build_size = re.search('项目总建筑面积：.*?<td>(.*?)</td>', con, re.S | re.M).group(1)
        comm.co_land_use = re.search('土地使用证号.*?<td>(.*?)<', con, re.S | re.M).group(1)
        comm.co_plan_pro = re.search('规划许可证号.*?<td>(.*?)<', con, re.S | re.M).group(1)
        comm.insert_db()

        build_id_list = re.findall("onclick=.doview\('(\d+)'\)", con, re.S | re.M)
        self.get_build_info(build_id_list, co_id)

    def get_build_info(self, build_id_list, co_id):
        bu = Building(co_index)
        for build_id in build_id_list:
            formdata = {}
            formdata["action"] = "qeurySingleBuilding"
            formdata['pk'] = str(build_id)
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
                'Referer': 'http://hkrealestate.haikou.gov.cn/wp_myself/housequery/projectBuildingList.php'
            }
            try:
                build_info = self.s.post('http://hkrealestate.haikou.gov.cn/wp_myself/housequery/projectBuildHouseAction.php', data=formdata, headers=header)
            except Exception as e:
                print("co_idnex={},楼栋错误".format(co_index),e)

            build_con = build_info.text
            bu.bu_id = build_id
            bu.co_id = co_id
            bu.bu_num = re.search('幢名称.*?<td>(.*?)<', build_con, re.S | re.M).group(1)
            bu.bu_floor = re.search('总层数.*?<td>(.*?)<', build_con, re.S | re.M).group(1)
            bu.bu_build_size = re.search('>建筑面积.*?<td>(.*?)<', build_con, re.S | re.M).group(1)
            bu.bo_develops = re.search('房地产企业.*?">(.*?)</td', build_con, re.S | re.M).group(1)

            bu.insert_db()

            self.get_house_info(build_con, co_id, build_id)

    def get_house_info(self, con, co_id, build_id):
        html_str = re.search('houseTableData.*?特别申明',con, re.S | re.M).group()
        for info in re.findall('<div style.*?</div>', html_str,re.S | re.M):
            try:
                ho = House(co_index)
                ho.ho_name = re.search("'HC_HOUSENUMB':'(.*?)',", info, re.S | re.M).group(1)
                ho.ho_room_type = re.search("'HC_HOUSETYPE':'(.*?)',", info, re.S | re.M).group(1)
                ho.ho_build_size = re.search("'HC_STCTAREA':'(.*?)',", info, re.S | re.M).group(1)
                ho.bu_id = build_id
                ho.co_id = co_id
                ho.insert_db()
            except Exception as e:
                print('house error, co_index={}'.format(co_index))
