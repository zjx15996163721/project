
"""
url = http://www.hcsfcglj.com/Templets/BoZhou/aspx/spflist.aspx
city : 河池
CO_INDEX : 16
author: 程纪文
"""


from backup.crawler_base import Crawler
from backup.comm_info import Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree

co_index = '16'
city = '河池'

class Hechi(Crawler):
    def __init__(self):
        self.url = 'http://www.hcsfcglj.com/Templets/BoZhou/aspx/spflist.aspx'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            # 'Cookie': 'ASP.NET_SessionId=lllitzrxbio3mh2s1gpmrhmg',
            'Referer': 'http://www.hcsfcglj.com/Templets/BoZhou/aspx/spflist.aspx'
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=self.url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='共.*?Count">(\d+)</span>页',
                       )
        page = b.get_page_count()
        formdata = {}
        for i in range(1,int(page)+1):
            formdata["__EVENTTARGET"] = "navigate$LnkBtnGoto"
            formdata["navigate$txtNewPageIndex"] = i
            try:
                res = requests.post(self.url,headers=self.headers)
            except Exception as e:
                print("co_index={},第{}页翻页失败".format(co_index,i))
                print(e)
                continue
            con = etree.HTML(res.text)
            formdata["__VIEWSTATE"] = con.xpath("//input[@id='__VIEWSTATE']/@value")[0]
            formdata["__EVENTVALIDATION"] = con.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]

            bu_url_list = con.xpath("//td[@style='width:13%']/a/@href")
            bu_pre = con.xpath("//td[@style='width:13%']/a/text()")
            bu_dev = con.xpath("//td[@style='width:24%']/text()")
            co_name = con.xpath("//td[@style='width:15%']/text()")
            # print(i)
            for index in range(len(bu_url_list)):
                bu_detail = "http://www.hcsfcglj.com/Templets/BoZhou/aspx/" + bu_url_list[index]
                bu_pre_sale = bu_pre[index]
                bo_develops = bu_dev[index]
                bu_co_name = co_name[index]
                try:
                    bu_res = requests.get(bu_detail,headers=self.headers)
                except Exception as e:
                    print("co_index={},楼栋{}无法访问".format(co_index,bu_detail))
                    print(e)
                    continue
                bu_con = bu_res.text

                self.get_build_info(bu_pre_sale,bo_develops,bu_co_name,bu_con)
                self.get_house_info(bu_con)



    def get_build_info(self,bu_pre_sale,bo_develops,bu_co_name,bu_con):

        build = Building(co_index)

        build.bu_id = re.search('编号.*?>(\d+)<',bu_con,re.S|re.M).group(1)
        build.bu_num = re.search('幢号.*?>(\d+)<',bu_con,re.S|re.M).group(1)
        build.bu_floor = re.search('总层数.*?>(\d+)<',bu_con,re.S|re.M).group(1)
        build.bu_build_size = re.search('预售建筑面积.*?>(\d+.\d+)<',bu_con,re.S|re.M).group(1)
        build.bu_address = re.search('楼房坐落.*?;">(.*?)</span',bu_con,re.S|re.M).group(1)
        build.bu_live_size = re.search('住宅建筑面积.*?>(\d+.\d+)<',bu_con,re.S|re.M).group(1)
        build.bu_not_live_size = re.search('非住宅建筑面积.*?;">(.*?)</span',bu_con,re.S|re.M).group(1)
        build.bo_build_start_time = re.search('开工日期.*?;">(.*?)</span',bu_con,re.S|re.M).group(1)
        build.bu_all_house = re.search('总套数.*?>(\d+)<',bu_con,re.S|re.M).group(1)
        build.bu_pre_sale = bu_pre_sale
        build.bo_develops = bo_develops
        build.co_name = bu_co_name
        build.insert_db()

    def get_house_info(self,bu_con):
        bu_html = etree.HTML(bu_con)
        house = House(co_index)
        ho = bu_html.xpath("//tr[@height='30']//span/a")
        bu_id = re.search('编号.*?>(\d+)<',bu_con,re.S|re.M).group(1)
        for ho_info in ho:
            try:
                ho_detail = "http://www.hcsfcglj.com/Templets/BoZhou/aspx/" + ho_info.xpath("./@value")[0]
                try:
                    ho_res = requests.get(ho_detail,headers=self.headers)
                    ho_con = ho_res.text
                except Exception as e:
                    print("co_index={},房屋详情页{}请求失败".format(co_index,ho_detail))
                    print(e)
                    continue
                house.ho_name = re.search('房号.*?<td>(.*?)<',ho_con,re.S|re.M).group(1)
                house.ho_floor = re.search('所在层.*?<td>(.*?)<',ho_con,re.S|re.M).group(1)
                house.ho_share_size = re.search('分摊共有面积.*?<td>(.*?)<',ho_con,re.S|re.M).group(1)
                house.ho_build_size = re.search('建筑面积.*?<td>(.*?)<',ho_con,re.S|re.M).group(1)
                house.ho_true_size = re.search('套内面积.*?<td>(.*?)<',ho_con,re.S|re.M).group(1)
                house.ho_type = re.search('房屋用途.*?<td>(.*?)<',ho_con,re.S|re.M).group(1)
                house.bu_num = re.search('幢号.*?<td>(.*?)<',ho_con,re.S|re.M).group(1)
                house.bu_id = bu_id
            except:
                house.ho_name = ho_info.xpath("./@id")[0]
                house.bu_id = bu_id

            house.insert_db()