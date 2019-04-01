"""
url = http://www.wxhouse.com:9097/wwzs/showIndex.action
city :  无锡
CO_INDEX : 163
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, House
import re, requests
from lxml import etree
from lib.log import LogHandler
import time

co_index = '163'
city_name = '无锡'
log = LogHandler('无锡')

class Wuxi(Crawler):
    def __init__(self):
        self.start_url = 'http://www.wxhouse.com:9097/wwzs/showIndex.action'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        post_url = 'http://www.wxhouse.com:9097/wwzs/getzxlpxx.action'
        index_res = requests.get(post_url,headers=self.headers)
        page = re.search('page.totalPageCount" value="(\d+)"',index_res.text).group(1)
        for i in range(1,int(page)+1):
            data = {
                'page.currentPageNo':i,
                'page.pageSize': 15,
                'page.totalPageCount': page,
            }
            try:
                res = requests.post(post_url,headers=self.headers,data=data)
                html = etree.HTML(res.content.decode())
            except:
                log.error("翻页请求失败")
                continue
            temp_list = html.xpath("//table//td/a")
            for i in temp_list:
                try:
                    temp_url = i.xpath("./@href")[0]
                    com_url = "http://www.wxhouse.com:9097"+temp_url
                    com_res = requests.get(com_url,headers=self.headers)
                    content = com_res.content.decode()
                    co = Comm(co_index)
                    co.co_id = re.search('id=(\d+)',temp_url).group(1)
                    co.co_name = re.search('项目现定名.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_pre_sale = re.search('预（销）售许可证号.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_develops = re.search('商:</td>.*?;">(.*?)</a',content,re.S|re.M).group(1)
                    co.co_address = re.search('落:</td>.*?">(.*?)</td',content,re.S|re.M).group(1)
                    area = re.search('行政区:.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.area = area.strip()
                    co.co_land_use = re.search('土地证号:.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_plan_pro = re.search('规划许可证号:.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_plan_useland = re.search('用地许可证号:.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_work_pro = re.search('施工许可证号:.*?">(.*?)</td',content,re.S|re.M).group(1)
                    co.co_all_house = re.search('总套数.*?">(\d+)&nbsp',content,re.S|re.M).group(1)
                    co.insert_db()
                except:
                    log.error("{}小区解析失败".format(com_url))
                    continue

                detail = re.search('楼盘概况.*?href="(.*?)".*?房屋明细',content,re.S|re.M).group(1)
                self.detail_parse(detail,co.co_id)

    def detail_parse(self,detail,co_id):
        detail_url = 'http://www.wxhouse.com:9097'+detail
        try:
            get_res = requests.get(detail_url,headers=self.headers)
        except:
            return
        page = re.search('page.totalPageCount" value="(\d+)"',get_res.content.decode()).group(1)
        for i in range(1,int(page)+1):
            data = {
                'page.currentPageNo': i,
                'page.pageSize': 20,
                'page.totalPageCount': page,
            }
            detail_res = requests.post(detail_url,headers=self.headers,data=data)
            detail_html = etree.HTML(detail_res.content.decode())
            house_list = detail_html.xpath("//table//td[@align='left']/a")
            for house in house_list:
                try:
                    house_url = "http://www.wxhouse.com:9097" + house.xpath("./@href")[0]
                    ho_res = requests.get(house_url,headers=self.headers)
                    content = ho_res.content.decode()
                    ho = House(co_index)
                    ho.co_id = co_id
                    ho.bu_num = re.search('幢号.*?">(.*?)&nbsp',content,re.S|re.M).group(1).strip()
                    ho.ho_name = re.search('室号.*?">(.*?)&nbsp',content,re.S|re.M).group(1).strip()
                    ho.unit = re.search('单元号.*?">(.*?)&nbsp',content,re.S|re.M).group(1).strip()
                    ho.ho_type = re.search('用途.*?">(.*?)</td',content,re.S|re.M).group(1).strip()
                    ho.ho_build_size = re.search('总面积.*?">(.*?)&nbsp',content,re.S|re.M).group(1).strip()
                    ho.ho_true_size = re.search('套内面积.*?">(.*?)&nbsp',content,re.S|re.M).group(1).strip()
                    ho.ho_share_size = re.search('分摊面积.*?">(.*?)&nbsp',content,re.S|re.M).group(1).strip()
                    ho.ho_floor = re.search('所在层.*?">(.*?)&nbsp',content,re.S|re.M).group(1).strip()
                    ho.ho_price = re.search('报价.*?red">(.*?)&nbsp',content,re.S|re.M).group(1).strip()
                    ho.insert_db()
                except Exception as e:
                    log.error("{}房屋未能解析{}".format(house_url,e))
                    continue
                time.sleep(2)

