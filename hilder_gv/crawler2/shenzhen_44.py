"""
url = http://ris.szpl.gov.cn/bol/index.aspx
city : 深圳
CO_INDEX : 44
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree
from urllib import parse

co_index = 44


class Shengzhen(Crawler):
    def __init__(self):
        self.start_url = "http://ris.szpl.gov.cn/bol/index.aspx"
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
            'Referer':
                'http://ris.szpl.gov.cn/bol/index.aspx',
            'Cookie':
                'ASP.NET_SessionId=lnxo1v45s03n1i452x3cv53l',
            'Host':
                'ris.szpl.gov.cn',
            'Origin':
                'http://ris.szpl.gov.cn',
            # 'Upgrade-Insecure-Requests':'1',

            # 'Content-Length': '7171',
            # 'Content-Type': 'application/x-www-form-urlencoded',
            # 'Proxy-Connection': 'keep-alive',

               }
    def start_crawler(self):
        b = AllListUrl(first_page_url=self.start_url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='gbk',
                       page_count_rule='总共<b>(\d+)<',
                       )
        page = b.get_page_count()

        formdata = {}
        comm_url_list = []
        for i in range(1, int(page) + 1):

            res = requests.post(self.start_url, data=formdata,)
            con  = res.content.decode('gbk')
            con = etree.HTML(con)
            view_state = con.xpath("//input[@name='__VIEWSTATE']/@value")[0]
            valid = con.xpath("//input[@name='__EVENTVALIDATION']/@value")[0]
            view_state = parse.quote_plus(view_state,encoding='gbk')
            valid = parse.quote_plus(valid,encoding='gbk')
            formdata["__VIEWSTATE"] = view_state  # 保存当前页的信息作为下一页请求参数
            formdata["__EVENTVALIDATION"] = valid
            formdata["__EVENTTARGET"] = 'AspNetPager1'
            formdata["__VIEWSTATEGENERATOR"] = "248CD702"
            formdata["__EVENTARGUMENT"] = str(i+1)
            formdata["AspNetPager1_input"] = str(i)

            url_list = con.xpath("//tr[@bgcolor='#F5F9FC']/td[@bgcolor='white']/a/@href")
            comm_url_list.extend(url_list)
        self.comm_info(comm_url_list)

    def comm_info(self, comm_url_list):  # 小区信息
        co = Comm(co_index)
        build_url_list = []
        for comm_url in comm_url_list:
            co.co_id = re.search('id=(\d+)', comm_url).group(1)
            detail_url = "http://ris.szpl.gov.cn/bol/" + comm_url.lstrip(".")
            url = "http://ris.szpl.gov.cn/bolprojectdetail.aspx?id=" + str(co.co_id)
            try:
                res = requests.get(detail_url, headers=self.headers)
                con = res.text

                co.co_pre_sale = re.search('许可证号.*?">(.*?)&', con).group(1)
                co.co_name = re.search('项目名称.*?">(.*?)&', con).group(1)
                co.co_address = re.search('所在位置.*?">(.*?)&', con).group(1)
                co.co_develops = re.search('发展商.*?">(.*?)&', con).group(1)
                co_type = re.search('住宅.*?面积.*?">(.*?)平方米.*?套数.*?">(.*?)&', con)
                co.co_build_size = co_type.group(1)
                co.co_all_house = co_type.group(2)
                co.insert_db()

                response = requests.get(url, headers=self.headers)
                content = etree.HTML(response.text)
                build_url = content.xpath("//td/a/@href")
                build_url_list.extend(build_url)
            except:
                continue
        self.build_info(build_url_list)

    def build_info(self, build_url_list):
        bu = Building(co_index)

        for build_url in build_url_list:
            url = "http://ris.szpl.gov.cn/bol/" + build_url
            res = requests.get(url, headers=self.headers)
            con = etree.HTML(res.text)
            branch_list = con.xpath("//div[@id='divShowBranch/a/@href")
            for branch in branch_list:
                branch_url = "http://ris.szpl.gov.cn/bol/" + branch
                response = requests.get(branch_url, headers=self.headers)

                content = etree.HTML(response.text)
                bu.bu_num = content.xpath("//div[@id='curAddress']/a/text()")[2]
                bu.co_name = content.xpath("//div[@id='curAddress']/a/text()")[1]
                co_info = content.xpath("//form/@action")[0]
                bu.bu_id = bu_id = re.search('\?id=(\d+)&', co_info).group(1)
                bu.co_id = co_id = re.search('presellid=(\d+)&', co_info).group(1)

                bu.insert_db()
                house_list = content.xpath("//div[@id='updatepanel1']//tr[@class='a1']//a/@href")[2:-1]

                self.house_info(house_list, bu_id, co_id)


    def house_info(self, house_list, bu_id, co_id):
        ho = House(co_index)
        for house_url in house_list:
            url = "http://ris.szpl.gov.cn/bol/" + house_url
            res = requests.get(url, headers=self.headers)
            ho.ho_num = re.search('id=(\d+)', house_url).group(1)
            con = res.text
            ho.bu_num = re.search('情况.*?">(.*?)&', con).group(1)
            ho.bu_id = bu_id
            ho.co_id = co_id
            ho.ho_floor = re.search('楼层.*?">(\d+)&', con).group(1)
            ho.ho_num = re.search('房号.*?">(\d+)&', con).group(1)
            ho.ho_type = re.search('用途.*?">(\d+)&', con).group(1)
            ho.ho_room_type = re.search('户型.*?">(\d+)&', con).group(1)
            ho.ho_build_size = re.search('建筑面积<.*?">(\d+.\d+)平方米', con).group(1)
            ho.ho_true_size = re.search('户内面积<.*?">(\d+.\d+)平方米', con).group(1)
            ho.insert_db()


if __name__ == '__main__':
    shenzheng = Shengzhen()
    shenzheng.start_crawler()
