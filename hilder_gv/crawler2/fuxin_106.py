"""
url = http://www.fxfdcw.com/searchhouse.asp
city :  阜新
CO_INDEX : 106
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
from lxml import etree
from lib.log import LogHandler

co_index = '106'
city = '阜新'
log = LogHandler('fuxin_106')

class Fuxin(Crawler):
    def __init__(self):
        self.start_url = 'http://www.fxfdcw.com/searchhouse.asp'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        data = {
            "Submit":"(unable to decode value)"
        }
        res = requests.post(self.start_url,data=data,headers=self.headers)
        html = etree.HTML(res.content.decode('gbk'))
        comm_url_list = html.xpath("//tr//span[@style='width:270px; color:#006']//a/@href")
        for comm_url in comm_url_list:
            try:
                url = 'http://www.fxfdcw.com/' + comm_url
                com_res = requests.get(url,headers=self.headers)
                con = com_res.content.decode('gbk')
                co = Comm(co_index)
                co.co_id = re.search('xmid=(\d+)',comm_url).group(1)
                co.co_name =  re.search('项目名称.*?">(.*?)</',con,re.S|re.M).group(1)
                co.co_develops = re.search('开发企业:(.*?) &nbsp',con,re.S|re.M).group(1)
                co.co_address = re.search('项目地址.*?">(.*?)</',con,re.S|re.M).group(1)
                co.co_build_size = re.search('建筑面积.*?">(.*?)</',con,re.S|re.M).group(1)
                co.co_all_house = re.search('总套数.*?">(.*?)</',con,re.S|re.M).group(1)
                co.insert_db()

                bu_list = re.findall("window.open\('(.*?)'\)",con,re.S|re.M)
            except Exception as e:
                # log.error("小区信息错误{}".format(e))
                print("小区信息错误{}".format(e))
                continue

            self.bu_info(bu_list,co.co_id)

    def bu_info(self,bu_list,co_id):
        for bu in bu_list:
            try:
                bu_url = 'http://www.fxfdcw.com/'+bu
                res = requests.get(bu_url,headers=self.headers)
                con = res.content.decode('gbk')
                html = etree.HTML(con)
                build = Building(co_index)
                build.co_id = co_id
                build.bu_id = re.search('bdid=(\d+)',bu).group(1)
                build.bu_num = re.search('楼号.*?">(.*?)</',con,re.S|re.M).group(1)
                build.bu_address =  re.search('坐落.*?">(.*?)</',con,re.S|re.M).group(1)
                build.bu_floor = re.search('地上层数.*?">(.*?)</',con,re.S|re.M).group(1)
                build.bu_build_size = re.search('建筑面积.*?wrap">(.*?)</',con,re.S|re.M).group(1)
                build.bu_all_house = re.search('套 数.*?">(.*?)</',con,re.S|re.M).group(1)
                build.bu_type = re.search('用　　途.*?wrap">(.*?)</',con,re.S|re.M).group(1)
                build.insert_db()

                ho_list = html.xpath("//span[@title]")
            except Exception as e:
                # log.error("楼栋信息错误{}".format(e))
                print("楼栋信息错误{}".format(e))
                continue
            self.ho_info(ho_list,co_id,build.bu_id)

    def ho_info(self,ho_list,co_id,bu_id):
        for hou in ho_list:
            try:
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = hou.xpath("./text()")[0]
                ho_info = hou.xpath("./@title")[0]
                ho.ho_build_size = re.search('建筑面积:(.*?)\n',ho_info).group(1)
                ho.ho_share_size = re.search('分摊面积:(.*)',ho_info).group(1)
                ho.ho_true_size = re.search('套内面积:(.*?)\n',ho_info).group(1)
                ho.insert_db()
            except Exception as e:
                # log.error("房屋信息错误{}".format(e))
                print("房屋信息错误{}".format(e))





