"""
url = http://www.sxyqfdc.com:85/More_xm.aspx
city :  阳泉
CO_INDEX : 62
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.producer import ProducerListUrl
import re, requests

co_index = '62'
city = '阳泉'

class Yangquan(Crawler):
    def __init__(self):
        self.url = "http://www.sxyqfdc.com:85/"
        self.headers = {'User-Agent':
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36', }
        self.page = 7
    def start_crawler(self):
        for i in range(1,self.page+1):
            url = self.url +"More_xm.aspx?page=" +str(i)
            p = ProducerListUrl(page_url=url,
                                request_type='get', encode='utf-8',
                                analyzer_rules_dict=None,
                                current_url_rule="//td[@align='left']/a/@href",
                                analyzer_type='xpath',
                                headers=self.headers)
            comm_url_list = p.get_current_page_url()
            self.get_comm_info(comm_url_list)

    def get_comm_info(self,comm_url_list):
        for comm_url  in comm_url_list:
            url = self.url + comm_url
            try:
                res = requests.get(url,headers=self.headers)
            except Exception as e:
                print("co_index={},小区信息错误".format(co_index),e)
                continue
            con = res.text
            co = Comm(co_index)
            co.co_id = re.search('Id=(\d+)',comm_url).group(1)
            co.co_name = re.search('项目名称.*?Name">(.*?)</span',con,re.S|re.M).group(1)
            co.co_develops = re.search('开发商.*?Name">(.*?)</span',con,re.S|re.M).group(1)
            co.co_address = re.search('地址.*?Address">(.*?)</span',con,re.S|re.M).group(1)
            co.co_build_size = re.search('建筑面积.*?jzmj">(.*?)</span',con,re.S|re.M).group(1)
            co.co_type = re.search('项目类型.*?Type">(.*?)</span',con,re.S|re.M).group(1)
            co.co_size = re.search('占地面积.*?mzgm">(.*?)</span',con,re.S|re.M).group(1)
            co.co_green = re.search('绿化率.*?Jdl">(.*?)</span',con,re.S|re.M).group(1)
            co.co_volumetric = re.search('容积率.*?Rjl">(.*?)</span',con,re.S|re.M).group(1)
            co.co_build_start_time = re.search('开工日期.*?kgrq">(.*?)</span',con,re.S|re.M).group(1)
            co.co_build_end_time = re.search('竣工日期.*?syrq">(.*?)</span',con,re.S|re.M).group(1)

            co.insert_db()
            presell_url_list = re.findall('【<a href="(.*?)" target="_self"',con,re.S|re.M)
            self.get_build_info(presell_url_list,co.co_id)

    def get_build_info(self,presell_url_list,co_id):
        for presell_url in presell_url_list:
            pre_url = self.url + presell_url
            res = requests.get(pre_url,headers=self.headers)
            build_url_list = re.findall('【<a href="(.*?)" target="_self"',res.text,re.S|re.M)
            for build_url in build_url_list:
                build_info_url = self.url+build_url
                try:
                    build_res = requests.get(build_info_url,headers=self.headers)
                    con = build_res.text
                    bu = Building(co_index)
                    bu.co_id = co_id
                    bu.bu_id = re.search('ID=(\d+)',build_url).group(1)
                    bu.bu_num = re.search('栋.*?号.*?BuildingName">(.*?)</span',con,re.S|re.M).group(1)
                    bu.bu_floor = re.search('总 层 数.*?(\d+)</span',con,re.S|re.M).group(1)
                    bu.bu_build_size = re.search('建筑面积.*?Jzmj">(.*?)</span',con,re.S|re.M).group(1)
                    bu.bu_live_size = re.search('住宅面积.*?Zzmj">(.*?)</span',con,re.S|re.M).group(1)
                    bu.bu_not_live_size = re.search('非住宅面积.*?Fzzmj">(.*?)</span',con,re.S|re.M).group(1)
                    bu.bu_pre_sale = re.search('预售许可证.*?xkzh">(.*?)</span',con,re.S|re.M).group(1)
                    bu.bu_pre_sale_date = re.search('发证日期.*?fzrq">(.*?)</span',con,re.S|re.M).group(1)
                    bu.bu_type = re.search('项目类型.*?Type">(.*?)</span',con,re.S|re.M).group(1)
                    bu.insert_db()
                except Exception as e:
                    print("co_index={},楼栋信息错误".format(co_index), e)
                    continue
                house_detail_list = re.findall("getMoreHouseInfo\('(.*?)'\)\"",con,re.S|re.M)
                self.get_house_info(co_id,bu.bu_id,house_detail_list)

    def get_house_info(self,co_id,bu_id,house_detail_list):
        for house_detail in house_detail_list:
            house_url = self.url + house_detail
            try:
                house_res = requests.get(house_url,headers=self.headers)
                house_res.status_code == 200
            except Exception as e:
                print("co_index={},房屋信息错误".format(co_index),e)
                continue
            house_con = house_res.text

            ho = House(co_index)
            ho.co_id = co_id
            ho.bu_id = bu_id
            ho.ho_name = re.search('房号.*?fh">(.*?)</span',house_con,re.S|re.M).group(1)
            ho.orientation = re.search('朝向.*?Cx">(.*?)</span',house_con,re.S|re.M).group(1)
            ho.ho_floor = re.search('层.*?lc">(.*?)</span',house_con,re.S|re.M).group(1)
            ho.ho_room_type = re.search('房型.*?hx">(.*?)</span',house_con,re.S|re.M).group(1)
            ho.ho_build_size = re.search('建筑面积.*?jzmj">(.*?)</span',house_con,re.S|re.M).group(1)
            ho.ho_share_size = re.search('分摊面积.*?ftmj">(.*?)</span',house_con,re.S|re.M).group(1)
            ho.ho_true_size= re.search('套内面积.*?tnmj">(.*?)</span',house_con,re.S|re.M).group(1)
            ho.ho_type = re.search('用途.*?lx">(.*?)</span',house_con,re.S|re.M).group(1)

            ho.insert_db()



