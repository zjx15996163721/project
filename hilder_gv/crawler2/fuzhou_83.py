"""
url = http://222.77.178.63:7002/result_new.asp
city :  福州
CO_INDEX : 83
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
import re, requests
from lxml import etree
from urllib import parse
from lib.log import LogHandler

co_index = '83'
city = '福州'

log = LogHandler('fuzhou_83')

class Fuzhou(Crawler):
    def __init__(self):
        self.start_url = 'http://222.77.178.63:7002/result_new.asp'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        b = AllListUrl(first_page_url=self.start_url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='gbk',
                       page_count_rule='共(\d+)页',
                       )
        page = b.get_page_count()
        for i in range(1,int(page+1)):
            url = self.start_url + '?page2=' + str(i)
            res = requests.get(url,headers=self.headers)
            html = etree.HTML(res.content.decode('gbk'))
            comm_url_list = html.xpath("//td/a[@target]/@href")
            self.comm_info(comm_url_list)

    def comm_info(self,comm_url_list):
        for comm_url in comm_url_list:
            try:
                co_url = 'http://222.77.178.63:7002/' + comm_url
                co_res = requests.get(co_url,headers=self.headers)
                con = co_res.content.decode('gbk')
                co = Comm(co_index)
                co.co_id = re.search('projectID=(.*)',comm_url).group(1)
                co.co_name = re.search('项目名称：.*?">(.*?)</',con,re.S|re.M).group(1)
                co.area = re.search('所在区县：.*?">(.*?)</',con,re.S|re.M).group(1)
                co.co_address = re.search('项目地址：.*?">(.*?)</',con,re.S|re.M).group(1)
                co.co_develops = re.search('企业名称：.*?blank">(.*?)</',con,re.S|re.M).group(1)
                co.co_all_house = re.search('>总套数.*?">(\d+)<',con,re.S|re.M).group(1)
                co.co_all_size = re.search('>总面积.*?">(.*?)<',con,re.S|re.M).group(1)
                project_name = parse.quote(co.co_name)
                co.insert_db()
            except Exception as e:
                # log.error('小区信息错误{}'.format(e))
                print('小区信息错误{}'.format(e))

            sale_url = "http://222.77.178.63:7002/Presell.asp?projectID=" +co.co_id + "&projectname=" + project_name
            res = requests.get(sale_url,headers=self.headers)
            html = etree.HTML(res.content.decode('gbk'))
            temp_url_list = html.xpath("//a/@href")
            self.build_info(co.co_id,temp_url_list)

    def build_info(self,co_id,temp_url_list):
            for temp_url in temp_url_list:
                try:
                    build_url = "http://222.77.178.63:7002/" + temp_url
                    res = requests.get(build_url,headers=self.headers)
                    html = etree.HTML(res.content.decode('gbk'))
                    build_info_list = html.xpath("//tr[@class='indextabletxt']")
                    for build_info in build_info_list:
                        bu = Building(co_index)
                        ho_url = build_info.xpath("./td/a/@href")[0]
                        bu.co_id = co_id
                        bu.bu_id = re.search('Param=(.*)',ho_url).group(1)
                        bu.bu_num = build_info.xpath("./td/a/text()")[0]
                        bu.bu_all_house = build_info.xpath("./td[2]/text()")[0]
                        try:
                            bu.bu_all_size = build_info.xpath("./td[3]/text()")[0]
                        except:
                            bu.bu_all_size  = None
                        try:
                            bu.bu_live_size = build_info.xpath("./td[5]/text()")[0]
                        except:
                            bu.bu_live_size = None
                        bu.insert_db()
                except Exception as e:
                    # log.error('楼栋信息错误{}'.format(e))
                    print('楼栋信息错误{}'.format(e))
                    continue
                self.house_info(ho_url,co_id,bu.bu_id)

    def house_info(self,ho_url,co_id,bu_id):
        url = "http://222.77.178.63:7002/" + ho_url
        url.rstrip('=')
        res = requests.get(url,headers=self.headers)
        res.encoding = 'gbk'
        html = etree.HTML(res.text)
        house_detail_list = html.xpath("//td/a[@target]/@href")
        for house_detail in house_detail_list:
            try:
                detail_url = "http://222.77.178.63:7002/" + house_detail
                detail_res = requests.get(detail_url,headers=self.headers)
                detail_res.encoding = 'gbk'
                con = detail_res.text
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_name = re.search('室号.*?">(.*?)<',con,re.S|re.M).group(1)
                ho.ho_floor = re.search('实际层.*?">(.*?)<',con,re.S|re.M).group(1)
                ho.ho_type = re.search('房屋类型.*?">(.*?)<',con,re.S|re.M).group(1)
                ho.ho_build_size = re.search('预测建筑面积.*?">(.*?)<',con,re.S|re.M).group(1)
                ho.ho_true_size = re.search('预测套内面积.*?">(.*?)<',con,re.S|re.M).group(1)
                ho.ho_share_size = re.search('预测分摊面积.*?">(.*?)<',con,re.S|re.M).group(1)
                ho.ho_price = re.search('总价.*?">(.*?)<',con,re.S|re.M).group(1)
                ho.insert_db()
            except Exception as e:
                # log.error('房屋信息错误{}'.format(e))
                print('房屋信息错误{}'.format(e))






