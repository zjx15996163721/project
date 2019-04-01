"""
url = http://ys.tyfdc.gov.cn/Firsthand/tyfc/publish/p/ProjectList.do
city : 太原
CO_INDEX : 49
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
import json
from multiprocessing import Process, Queue

co_index = 49
count = 0
city = '太原'


class Taiyuan(Crawler):
    def __init__(self):
        self.start_url = "http://ys.tyfdc.gov.cn/Firsthand/tyfc/publish/getHouseUse.do"
        self.headers = {'User-Agent':
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36', }

    def crawler(self, url_list):
        res = requests.get(self.start_url, headers=self.headers)
        con = json.loads(res.text)
        house_type_list = con
        url = "http://ys.tyfdc.gov.cn/Firsthand/tyfc/publish/ProjListForPassed.do"
        formdata = {}
        # url_list = Queue()
        for house_type_num in house_type_list:
              # 所有类型的小区
            formdata["HouseType"] = house_type_num["code"]
            formdata["pageSize"] = '15'
            formdata["pageNo"] = '1'
            b_page = requests.post(url, data=formdata, headers=self.headers)
            num = re.search('total:(\d+),', b_page.text).group(1)
            num = int(num)
            page = round(num / 50)
            for i in range(1, page + 1):  # 翻页请求
                formdata["pageSize"] = 50
                formdata["pageNo"] = i
                comm_url_res = requests.post(url, data=formdata, headers=self.headers)
                con = comm_url_res.text
                co_id_list = re.findall('objid="(.*?)"', con)
                co_area_list = re.findall('</a></td>\r\n<td>(.*?)区</td>', con, re.S | re.M)
                co_type = re.findall('区</td>\r\n<td>(.*?)</td>\r\n<td>\(', con, re.S | re.M)
                for index in range(0, len(co_id_list)):
                    co_id = co_id_list[index]
                    co_area = co_area_list[index]
                    type = co_type[index]
                    comm_url = "http://ys.tyfdc.gov.cn/Firsthand/tyfc/publish/p/PermitInfo.do?propid=" + co_id
                    url_list.put((comm_url, co_area, type))


    def comm_parse(self, url_list):  # 小区信息解析
        co = Comm(co_index)
        # url_list = Queue()
        while True:
            url, area, type = url_list.get()
            try:
                res = requests.get(url, headers=self.headers)
            except Exception as e:
                print("co_index={},小区详情页无法访问".format(co_index),e)
                continue
            con = res.text
            co.area = area
            co.co_type = type
            co.co_id = re.search('id=(\d+)', url).group(1)
            co.co_develops = re.search('企业名称.*?>&nbsp;(.*?)<', con, re.S | re.M).group(1)
            co.co_name = re.search('项目名称.*?>&nbsp;(.*?)<', con, re.S | re.M).group(1)
            co.co_address = re.search('项目座落.*?>&nbsp;(.*?)<', con, re.S | re.M).group(1)
            co.co_use = re.search('房屋用途.*?>&nbsp;(.*?)<', con, re.S | re.M).group(1)
            try:
                co.co_pre_sale = re.search('许可证号.*?>&nbsp;(.*?)<', con, re.S | re.M).group(1)
            except:
                co.co_pre_sale = None
            new_url = "http://ys.tyfdc.gov.cn/Firsthand/tyfc/publish/p/ProjInfo.do?propid=" + co.co_id
            a_res = requests.get(new_url, headers=self.headers)
            a_con = a_res.text
            co.co_build_size = re.search('建筑面积.*?>&nbsp;(.*?)<', a_con, re.S | re.M).group(1)
            co.co_all_house = re.search('销售套数.*?>&nbsp;(.*?)<', a_con, re.S | re.M).group(1)
            co.co_green = re.search('绿化率.*?>&nbsp;(.*?)<', a_con, re.S | re.M).group(1)
            co.co_build_start_time = re.search('开工日期.*?>&nbsp;(.*?)<', a_con, re.S | re.M).group(1)
            co.co_build_end_time = re.search('竣工日期.*?>&nbsp;(.*?)<', a_con, re.S | re.M).group(1)
            co.co_volumetric = re.search('容积率.*?>&nbsp;(.*?)<', a_con, re.S | re.M).group(1)
            co.insert_db()
            global count
            count += 1
            print(count)
            try:
                self.build_parse(co.co_id,)
            except Exception as e:
                print("co_index={},楼栋信息错误".format(co_index),e)


    def build_parse(self, co_id):  # 楼栋信息解析
        bu = Building(co_index)
        build_info_url = "http://ys.tyfdc.gov.cn/Firsthand/tyfc/publish/ProNBList.do"
        formdata = {
            "pid": co_id,
            "pageNo": "1",
            "pageSize": "50"
        }
        res = requests.post(build_info_url, data=formdata, headers=self.headers)
        con = res.text
        info = re.findall('<tr objid.*?</tr>', con, re.S | re.M)
        for i in info:
            bu.co_id = co_id
            bu.bu_id = re.search('objid="(\d+)"', i).group(1)
            bu.bu_num = re.findall('<span>(.*?)<', i)[1]
            bu.bu_floor = re.search('<td>(\d+)\(', i).group(1)
            bu.bu_address = re.findall('<td>(.*?)</td>', i)[-1]
            bu.insert_db()
            self.house_parse(bu.bu_id, co_id)

    def house_parse(self, bu_id, co_id):  # 房屋信息解析
        ho = House(co_index)
        house_url = "http://ys.tyfdc.gov.cn/Firsthand/tyfc/publish/probld/NBView.do?"
        formdata = {
            "nid": bu_id,
            "projectid": co_id
        }
        try:
            res = requests.post(house_url, data=formdata, headers=self.headers)
        except Exception as e:
            print("co_index={},房屋详情页无法访问".format(co_index),e)
        con = res.text

        ho_name = re.findall('\'\);">(.*?)&nbsp;', con, re.S | re.M)
        ho_build_size = re.findall('<span.*?建筑面积：(.*?)㎡', con, re.S | re.M)
        ho_true_size = re.findall('<span.*?套内面积：(.*?)分', con, re.S | re.M)
        ho_share_size = re.findall('<span.*?分摊面积：(.*?)㎡', con, re.S | re.M)
        ho_type = re.findall('<span.*?用途：(.*?)房', con, re.S | re.M)
        ho_price = re.findall('<span.*?单价：(.*?)"', con, re.S | re.M)
        ho_id = re.findall("getHouseBaseInfo\('(.*?)'\)", con, re.S | re.M)
        for index in range(0, len(ho_id)):
            ho.co_id = co_id
            ho.bu_id = bu_id
            ho.ho_name = ho_name[index]
            ho.ho_build_size = ho_build_size[index]
            ho.ho_type = ho_type[index]
            ho.ho_share_size = ho_share_size[index]
            ho.ho_price = ho_price[index]
            ho.ho_true_size = ho_true_size[index]
            ho.ho_num = ho_id[index]
            ho.insert_db()

    def start_crawler(self):
        url_list = Queue()
        p1 = Process(target=self.crawler, args=(url_list,))
        p2 = Process(target=self.comm_parse, args=(url_list,))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
