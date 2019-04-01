"""
url = http://real.hffd.gov.cn/
city :  合肥
CO_INDEX : 168
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
import re, requests
import time
import json
import math
import random
from lxml import etree
from lib.log import LogHandler
from selenium.webdriver.chrome.options import Options

co_index = '168'
city_name = '合肥'
log = LogHandler('合肥')
chrome_options = Options()
chrome_options.add_argument('--headless')

class Hefei(Crawler):
    def __init__(self):
        self.start_url = 'http://real.hffd.gov.cn'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }
    def start_crawler(self):
        """
        无头chrome点击，可能出现无法点击的情况
        :return:
        """
        # driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver.get(self.start_url)
        # time.sleep(2)
        # elements = driver.find_elements_by_xpath("//span[@class='nav1']")
        # for element in elements:
        #     try:
        #         link = element.find_element_by_xpath('./a')
        #         id = link.get_attribute('id')
        #         link.get_attribute('onclick')
        #         link.click()
        #         windows = driver.window_handles
        #         driver.switch_to_window(windows[-1])
        #         data = driver.page_source
        #         driver.close()
        #         driver.switch_to_window(windows[0])
        #         self.project_info(data,id)
        #     except Exception as e:
        #         log.error("{}".format(e))
        #         continue
        # driver.quit()

        """
            js实现
        """
        indes_res = requests.get(self.start_url,headers=self.headers)
        html = etree.HTML(indes_res.text)
        id_list = html.xpath("//span/a/@id")
        iptstamp = html.xpath("//input[@id='iptstamp']/@value")[0]
        for id in id_list:
            new_id = self.js_handle(id,iptstamp)
            co_url = 'http://real.hffd.gov.cn/item/' + new_id
            co_res = requests.get(co_url,headers=self.headers)
            data = co_res.content.decode()
            self.project_info(data,id)
            log.info('{}已入库'.format(id))

    def project_info(self,data,id):
        try:
            co = Comm(co_index)
            co.id = id
            co.co_name = re.search(';<a href="#">(.*?)</a',data).group(1)
            co.co_develops = re.search('开发公司：</strong>(.*?)</dd',data).group(1)
            co.co_address = re.search('项目地址：</strong>(.*?)</dd',data).group(1)
            co.co_green = re.search('绿 化 率：</strong>(.*?)</dd>',data).group(1)
            co.co_volumetric = re.search('容 积 率：</strong>(.*?)</dd>',data).group(1)
            co.co_size = re.search('占地面积：</strong>(.*?)</dd',data).group(1)
            co.area = re.search('所属区域：</strong>(.*?)</dd',data).group(1)
            build_list = re.findall('<td>.*?</td>',data,re.S|re.M)
            co.insert_db()
        except Exception as e:
            log.error(e)
            return
        self.detail_parse(id,build_list)

    def detail_parse(self,id,build_list):
        for build in build_list:
            bu_temp = re.search('<a href="(.*?)"',build).group(1)
            build_url = self.start_url + bu_temp
            try:
                bu_res = requests.get(build_url,headers=self.headers)
                time.sleep(2)
                bu_text = bu_res.content.decode()
                bu = Building(co_index)
                bu.bu_num = re.search('幢号：(.*?) 许',bu_text).group(1)
                bu.bu_pre_sale = re.search('许可证号：<span>(.*?)</span>',bu_text).group(1)
                bu.bu_id = int(bu.bu_pre_sale)
                bu.bu_all_house = re.search('套数：<span>(.*?)</span',bu_text).group(1)
                bu.bu_floor = re.search('地上层数：<span>(.*?)</span',bu_text).group(1)
                bu.bo_build_end_time = re.search('竣工日期：<span>(.*?)</span',bu_text).group(1)
                bu.bu_build_size = re.search('预售许可面积：<span>(.*?)</span',bu_text).group(1)
                bu.bu_type = re.search('用途：<span>(.*?)</span',bu_text).group(1)
                bu.insert_db()
            except Exception as e:
                log.error("楼栋出错{}".format(e))
                continue
            self.house_detail(bu_text,id,bu.bu_id)

    def house_detail(self,bu_text,co_id,bu_id):
        html = etree.HTML(bu_text)
        house_idlist = html.xpath("//td[@class='cursor']/@onclick")
        for house_id in house_idlist:
            try:
                id = re.search('\d+',house_id).group(0)
                switch_id = self.nscaler(id)
                rsa_url = 'http://real.hffd.gov.cn/details/getrsa/' + switch_id
                house_res = requests.get(rsa_url,headers=self.headers)
                id_dict = json.loads(house_res.text)
                rsa = id_dict['id']
                house_url = 'http://real.hffd.gov.cn/details/house/' + rsa
                house_info = requests.get(house_url, headers=self.headers)
                house_detail = house_info.json()
                ho = House(co_index)
                ho.co_id = co_id
                ho.bu_id = bu_id
                ho.ho_room_type = house_detail['data']['lbHouseType']
                ho.ho_build_size = house_detail['data']['lbBuildArea']
                ho.ho_type = house_detail['data']['lbHouseUsefulness']
                ho.ho_true_size = house_detail['data']['lbInsideArea']
                ho.ho_share_size = house_detail['data']['lbJoinArea']
                ho.ho_name = house_detail['data']['lbPartNO']
                ho.ho_price =  house_detail['data']['iPrice']
                ho.insert_db()
            except Exception as e:
                log.error(e)
                continue

    def nscaler(self,id):
        """

        :param id: 首页小区a标签下的id or 时间戳
        :return: 混淆加密之后的id
        """
        password_dict = {
            '0':'0','1':'2','2':'5','3':'8','4':'6','5':'1','6':'3','7':'4','8':'9','9':'7',
        }
        i = ''
        for number in id:
            b = password_dict[number]
            i+=b
        return i

    def setobjnum(self,n):
        """

        :param n: id字符串长度
        :return:
        """
        i = 0
        a = ''
        while i<n:
            a+= str(math.floor(random.random()*10))
            i += 1
        return a

    def js_handle(self,id,stamp):
        """
        js方法
        :param id:  首页小区a标签下的id
        :param stamp: 首页中出现的时间戳
        :return: url中所需标记
        """
        m = self.nscaler(id)
        n = len(id)
        c = self.setobjnum(n)
        d = self.setobjnum(n)
        h = int(m) + int(d)
        b = self.nscaler(stamp)
        return c+"-"+str(h)+"-"+d+"-"+b