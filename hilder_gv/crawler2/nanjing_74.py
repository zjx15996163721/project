"""
url = http://www.njhouse.com.cn/2016/spf/list.php?saledate=&pgno=
city :  南京
CO_INDEX : 74
author: 程纪文
"""

from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re
from lxml import etree
from backup.proxy_connection import Proxy_contact
from lib.log import LogHandler

co_index = 74
city = '南京'
log = LogHandler('nanjing_74')

class Nanjing(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
        self.start_url = 'http://www.njhouse.com.cn/2016/spf/list.php?saledate=&pgno='

    def start_crawler(self):
        # res = requests.get(self.start_url,headers=self.headers)
        proxy = Proxy_contact(app_name="nanjing",method='get',url=self.start_url,headers=self.headers)
        # con = res.content.decode('gbk')
        con = proxy.contact()
        con = con.decode('gbk')
        page = re.search('共(.*?)页',con).group(1)

        for i in range(1,int(page)+1):
            url = self.start_url + str(i)
            # index_res = requests.get(url,headers=self.headers)
            proxy_page = Proxy_contact(app_name="nanjing", method='get', url=url,headers=self.headers)
            index_res = proxy_page.contact()
            index_res = index_res.decode('gbk')
            html = etree.HTML(index_res)
            comm_url_list = html.xpath("//td[@class='pp_img']//a/@href")
            self.comm_info(comm_url_list)

    def comm_info(self,comm_url_list):
        for temp in comm_url_list:
            comm_url = "http://www.njhouse.com.cn/2016/spf/"+temp
            try:
                co = Proxy_contact(app_name="nanjing", method='get', url=comm_url,headers=self.headers)
                co_res = co.contact()
            except Exception as e:
                log.error("小区页面访问失败{}".format(e))
                continue
            con = co_res.decode('gbk')
            comm = Comm(co_index)
            comm.co_id = re.search('prjid=(\d+)" ta',con).group(1)
            comm.co_name = re.search('<h2>(.*?)<em>',con).group(1)
            comm.area = re.search("\[.*?'>(.*?)</a>\]",con).group(1)
            comm.co_develops = re.search('开发企业</td>.*?">(.*?)</a',con,re.S|re.M).group(1)
            comm.co_address = re.search('项目地址.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            comm.co_open_time = re.search('开盘时间.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            comm.co_use = re.search('用途.*?<td>(.*?)</td',con,re.S|re.M).group(1)
            comm.co_pre_sale = re.findall("'_blank'>(\d+)</a>",con)
            # comm.co_land_use = re.search('土地使用.*?span>(.*?)</span',con,re.S|re.M).group(1)
            comm.co_plan_project =  re.search('工程规划.*?span>(.*?)</span',con,re.S|re.M).group(1)
            comm.co_plan_useland = re.search('用地规划.*?span>(.*?)</span',con,re.S|re.M).group(1)
            comm.co_work_pro = re.search('施工.*?span>(.*?)</span',con,re.S|re.M).group(1)
            comm.co_all_house = re.search('入网总套数.*?">(.*?)</td',con,re.S|re.M).group(1)
            comm.co_all_size =  re.search('入网总面积.*?td>(.*?)m',con,re.S|re.M).group(1)
            comm.insert_db()

            build_temp = "http://www.njhouse.com.cn/2016/spf/sales.php?prjid="+str(comm.co_id)
            while True:
                try:
                    build_proxy = Proxy_contact(app_name="nanjing", method='get', url=build_temp,headers=self.headers)
                    build_temp_con = build_proxy.contact()
                    build_temp_con = build_temp_con.decode('gbk')
                    html = etree.HTML(build_temp_con)
                    break
                except:
                    continue
            build_url_list = html.xpath("//div[@class='fdxs_left']/a/@href")
            self.build_info(build_url_list,comm.co_id)

    def build_info(self,build_url_list,co_id):
        for build_ in build_url_list:
            build_url = "http://www.njhouse.com.cn/2016/spf/"+ build_

            while True:
                build_pro = Proxy_contact(app_name="nanjing", method='get', url=build_url,headers=self.headers)
                build_con = build_pro.contact()
                build_con = build_con.decode('gbk')
                html = etree.HTML(build_con)
                bu = Building(co_index)
                bu.co_id = co_id
                try:
                    bu.bu_id = re.search('buildid=(\d+)', build_).group(1)
                    bu.bu_all_house = html.xpath("//tr[@class='yll']/td/text()")[1]
                    bu.bu_num = re.search('13px;">(.*?)&nbsp&nbsp', build_con).group(1)
                    bu.insert_db()
                    house_url_list = html.xpath("//td/a[1]/@href")
                    break
                except Exception as e:
                    log.error("楼栋请求失败{}".format(e))
                    continue

            self.house_info(co_id,bu.bu_id,house_url_list)

    def house_info(self,co_id,bu_id,house_url_list):
        for house_ in house_url_list:
            house_url = "http://www.njhouse.com.cn/2016/spf/" + house_
            try:
                # ho_res = requests.get(house_url,headers=self.headers)
                ho_pro = Proxy_contact(app_name="nanjing", method='get', url=house_url ,headers=self.headers)
                ho_con = ho_pro.contact()
                ho_con = ho_con.decode('gbk')

                # ho_con = ho_res.content.decode('gbk')
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = re.search('房号.*?;">(.*?)</td',ho_con,re.S|re.M).group(1)
                ho.ho_price = re.search('价格.*?<td>(.*?)元',ho_con,re.S|re.M).group(1)
                ho.ho_floor = re.search('楼层.*?;">(.*?)</td',ho_con,re.S|re.M).group(1)
                ho.ho_build_size = re.search('建筑面积.*?<td>(.*?)m',ho_con,re.S|re.M).group(1)
                ho.ho_true_size = re.search('套内面积.*?<td>(.*?)m',ho_con,re.S|re.M).group(1)
                ho.ho_share_size = re.search('分摊面积.*?<td>(.*?)m',ho_con,re.S|re.M).group(1)
                ho.ho_type = re.search('房屋类型.*?<td>(.*?)</td',ho_con,re.S|re.M).group(1)
            except Exception as e:
                log.error("房屋详情页错误{}".format(e))
                continue

            ho.insert_db()

