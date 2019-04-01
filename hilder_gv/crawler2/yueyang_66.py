from backup.crawler_base import Crawler
import requests
import re
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
from lxml import etree

co_index = "66"
city ='岳阳'

class Yueyang(Crawler):
    def __init__(self):
        self.url = 'http://xx.yyfdcw.com/NewHouse/BuildingList.aspx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=self.url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='1/(\d+)页',
                       )
        page = b.get_page_count()

        formdata={}
        for i in range(1,page+1):

            res = requests.post(self.url,data=formdata,headers=self.headers)
            html = etree.HTML(res.text)
            formdata["__EVENTTARGET"] = "Pager"
            formdata["__EVENTARGUMENT"] = str(i+1)
            formdata["__VIEWSTATEGENERATOR"] = "1D9D200C"
            formdata["__VIEWSTATE"] = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]

            comm_url_list = html.xpath("//h3/a/@href")
            self.get_comm_info(comm_url_list)

    def get_comm_info(self,comm_url_list):
        for comm_url in comm_url_list:
            comm_detail = "http://xx.yyfdcw.com"+comm_url
            try:
                comm_res = requests.get(comm_detail,headers=self.headers)
            except Exception as e:
                print("co_index={},小区详情页无法访问".format(co_index),e)
                continue
            con = comm_res.text
            comm = Comm(co_index)
            comm.co_id = re.search('ID=(\d+)',con).group(1)
            comm.co_name = re.search('lpname">.*?<h2>(.*?)</h2',con,re.S|re.M).group(1)
            comm.co_develops = re.search('开发商：.*?Kfs">(.*?)</span',con,re.S|re.M).group(1)
            comm.co_green = re.search('绿化率：.*?Lhl">(.*?)</span',con,re.S|re.M).group(1)
            comm.area = re.search('区域：.*?Name">(.*?)</span',con,re.S|re.M).group(1)
            comm.co_address = re.search('位置：</b>(.*?)</li',con,re.S|re.M).group(1)
            comm.co_build_size = re.search('建筑面积：.*?l5">(.*?)</span',con,re.S|re.M).group(1)
            comm.co_all_house = re.search('总户数：.*?hs">(.*?)</span',con,re.S|re.M).group(1)
            comm.co_plan_useland = re.search('用地.*?l4">(.*?)</span',con,re.S|re.M).group(1)
            comm.co_plan_project = re.search('工程.*?l3">(.*?)</span',con,re.S|re.M).group(1)
            comm.co_build_type = re.search('楼盘类型.*?Type">(.*?)</span',con,re.S|re.M).group(1)
            comm.co_all_size = re.search('占地面积.*?mianji">(.*?)</span',con,re.S|re.M).group(1)
            comm.co_land_use = re.search('使用权证.*?l1">(.*?)</span',con,re.S|re.M).group(1)

            comm.insert_db()
            try:
                build_list = re.findall('<td align="center">.*?<a href="(.*?)"',con,re.S|re.M)
                if len(build_list) > 0:
                    self.get_build_info(build_list, comm.co_id)
                else:
                    print("co_index={},小区co_id={}没有楼栋".format(co_index, comm.co_id))
                    continue
            except:
                print("co_index={},小区co_id={}没有楼栋".format(co_index,comm.co_id))
                continue


    def get_build_info(self,build_lis,co_id):
        for build_ in build_lis:
            build_url = "http://xx.yyfdcw.com"+build_
            try:
                build_res = requests.get(build_url,headers=self.headers)
            except Exception as e:
                print("co_index={},楼栋信息错误".format(co_index),e)
                continue
            con  = build_res.text
            bu = Building(co_index)
            bu.co_id = co_id
            bu.bu_id = re.search('Bid=(\d+)',build_).group(1)
            bu.bu_num = re.search('名称.*?">(.*?)</spa',con).group(1)
            bu.bu_pre_sale =  re.search("编.*?red'>(.*?)</a",con).group(1)
            bu.bu_pre_sale_date = re.search('颁发日期.*?Date">(.*?)</span',con).group(1)
            bu.bo_build_start_time = re.search('开工日期.*?">(.*?)</span',con).group(1)
            bu.bo_build_end_time = re.search('竣工日期.*?">(.*?)</span',con).group(1)
            bu.bo_develops = re.search('单位.*?">(.*?)</span',con).group(1)
            bu.bu_floor = re.search('层数.*?">(.*?)</span',con).group(1)
            bu.bu_live_size = re.search('住宅面积.*?">(.*?)</span',con).group(1)
            bu.size = re.search('总面积.*?">(.*?)</span',con).group(1)

            bu.insert_db()

            id = re.search('测量号.*?">(.*?)</span',con).group(1)
            self.get_house_info(co_id,bu.bu_id,id)

    def get_house_info(self,co_id,bu_id,id):

        house_list_url = "http://xx.yyfdcw.com/hetong/fdc_xxdxx.asp?id="+str(id)
        res = requests.get(house_list_url,headers=self.headers)
        con = res.content.decode('gbk')
        house_list = re.findall("onClick=.*?open\('(.*?)',", con,re.S | re.M)
        for house_ in house_list:
            try:
                house_url = "http://xx.yyfdcw.com/hetong/"+ house_
            except Exception as e:
                print("co_index={},房屋信息错误".format(co_index),e)
                continue
            ho_res = requests.get(house_url,headers=self.headers)
            ho_con = ho_res.content.decode('gbk')

            ho = House(co_index)
            ho.co_id = co_id
            ho.bu_id =bu_id
            ho.ho_name = re.search('室号.*?fafa>(.*?)</TD',ho_con,re.S|re.M).group(1)
            ho.ho_floor = re.search('实际层.*?fafa>(.*?)</TD',ho_con,re.S|re.M).group(1)
            ho.ho_build_size = re.search('建筑面积.*?fafa>(.*?)</TD',ho_con,re.S|re.M).group(1)
            ho.ho_true_size = re.search('套内面积.*?fafa>(.*?)</TD',ho_con,re.S|re.M).group(1)
            ho.ho_share_size = re.search('分摊面积.*?fafa>(.*?)</TD',ho_con,re.S|re.M).group(1)
            ho.ho_price = re.search('价格.*?fafa>(.*?)</TD',ho_con,re.S|re.M).group(1)
            ho.ho_type = re.search('用途.*?fafa>(.*?)</TD',ho_con,re.S|re.M).group(1)

            ho.insert_db()

