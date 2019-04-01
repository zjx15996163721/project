"""
url = http://www.hyfc365.com/RealEstate/RealtyProject/Search.aspx
city :  衡阳
CO_INDEX : 181
author: 程纪文
"""
from backup.crawler_base import Crawler
from backup.comm_info import Building, House
import re, requests
from lxml import etree
from lib.log import LogHandler

co_index = '181'
city_name = '衡阳'
log = LogHandler('衡阳')

class Hengyang(Crawler):
    def __init__(self):
        self.start_url = 'http://www.hyfc365.com/RealEstate/RealtyProject/Search.aspx'
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        viewstate = "/wEPDwUKLTM2MzMxMTM1Nw8WBB4PSGlkZUNvbnRleHRNZW51CymEAXprU3VwZXJNYXAuV2ViLlVJLnprU3VwZXJNYXBQYWdlU3R5bGUsIHprU3VwZXJNYXAuQ29tbW9uTGlicmFyeSwgVmVyc2lvbj0xLjEuNTAwLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49NzJkNzZkMzJkOGNiYTIyZgIeD0hpZGVTZWxlY3RTdGFydAsrBAIWAgIBD2QWCgIDD2QWAmYPDxYEHghDc3NDbGFzcwUQY3NzQm94VGl0bGVUaHJlZR4EXyFTQgICZBYCAgEPDxYGHgRUZXh0BRLlvIDlj5HkvIHkuJrmn6Xor6IeC05hdmlnYXRlVXJsBSQvUmVhbEVzdGF0ZS9SZWFsdHlEZWFsZXIvU2VhcmNoLmFzcHgeBlRhcmdldGUWAh4MVGV4dENoYW5naW5nBQRUcnVlZAIFD2QWAmYPDxYEHwIFFGNzc0JveFRpdGxlVGhyZWVPdmVyHwMCAmQWAgIBDw8WBh8EBRTmpbznm5go6aG555uuKeafpeivoh8FZR8GZRYCHwcFBFRydWVkAgcPZBYCZg8PFgQfAgUQY3NzQm94VGl0bGVUaHJlZR8DAgJkFgICAQ8PFgYfBAUUKOe9keS4iinmiL/mupDmn6Xor6IfBQUqL1JlYWxFc3RhdGUvUmVhbHR5U2VhcmNoL1NlYXJjaF9Ib3VzZS5hc3B4HwZlFgIfBwUEVHJ1ZWQCCQ9kFgJmDw8WBB8CBRBjc3NCb3hUaXRsZVRocmVlHwMCAmQWAgIBDw8WBh8EBRLlkIjlkIzlpIfmoYjmn6Xor6IfBQUsL1JlYWxFc3RhdGUvUmVhbHR5U2VhcmNoL1NlYXJjaF9SZWNvcmRzLmFzcHgfBmUWAh8HBQRUcnVlZAITDzwrAAsAZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUNQ3VzdG9tUGFnaW5nMbpNuvQVuP+DYqCe1+wbVab+715lNR+eC+hDFTSfvE0y"
        valid = "/wEWAwKHpppsAqi0zakHArrY8x1xs+nwBroCH5+KiDI9tW1jyttusdquHQRtH5UPs6GOzg=="
        data = {
            "CustomPaging1_CurrentPageIndex":-1,
            "__VIEWSTATE":viewstate,
            "__EVENTVALIDATION":valid,
            "hiddenInputToUpdateATBuffer_CommonToolkitScripts":1,
            "ButtonSearch":"%B2%E9+%D1%AF"
        }
        index_res = requests.post(self.start_url,headers=self.headers,data=data)
        page = re.search('页码.*?px;">(\d+)</td',index_res.text).group(1)
        self.page_turn(data,page,index_res)

    def page_turn(self,data,page,index_res):
        formdata = {}
        for i in range(1,int(page)+1):
            if i == 1:
                html = etree.HTML(index_res.content.decode('gbk'))
                self.parse(index_res)
                viewstate = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]
                valid = html.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]
                formdata = {
                    "CustomPaging1_CurrentPageIndex":0,
                    "__VIEWSTATE":viewstate,
                    "__EVENTVALIDATION":valid,
                    "hiddenInputToUpdateATBuffer_CommonToolkitScripts":1,
                    "ButtonSearch":"%B2%E9+%D1%AF",
                    "CustomPaging1_Numeric":2,
                }

            else:
                page_res = requests.post(self.start_url,data=formdata,headers=self.headers)
                viewstate = html.xpath("//input[@id='__VIEWSTATE']/@value")[0]
                valid = html.xpath("//input[@id='__EVENTVALIDATION']/@value")[0]
                formdata = {
                    "CustomPaging1_CurrentPageIndex": 0,
                    "__VIEWSTATE": viewstate,
                    "__EVENTVALIDATION": valid,
                    "hiddenInputToUpdateATBuffer_CommonToolkitScripts": 1,
                    "ButtonSearch": "%B2%E9+%D1%AF",
                    "CustomPaging1_Numeric": i+1,
                }
                self.parse(page_res)

    def parse(self,res):
        html = etree.HTML(res.content.decode('gbk'))
        bu_list = html.xpath("//div[@class='listCon']")
        for i in bu_list:
            temp = i.xpath("./a[@class='listCon2']/@href")[0]
            name = i.xpath("./a[@class='listCon1']/@title")[0]
            url = "http://www.hyfc365.com"+temp
            try:
                bu_res = requests.get(url,headers=self.headers)
                content = bu_res.content.decode('gbk')
                bu = Building(co_index)
                bu.bu_num = name
                project_id = re.search('ID=(.*)',temp).group(1)
                bu.bu_pre_sale = re.search('预售证名称.*?NAME">(.*?)</span',content,re.S|re.M).group(1)
                bu.bu_pre_sale_date = re.search('申领时间.*?">(.*?)</span',content,re.S|re.M).group(1)
                bu.bo_develops = re.search('申领单位.*?">(.*?)</span',content,re.S|re.M).group(1)
                bu.bu_build_size = re.search('"SALE_HOUSE_AREA">(.*?)<',content,re.S|re.M).group(1)
                bu.bu_all_house = re.search('"SALE_HOUSE_COUNT">(.*?)<',content,re.S|re.M).group(1)

                detail_url = 'http://www.hyfc365.com/RealEstate/Project/BuildingList.aspx?ID=' + project_id
                detail_res = requests.get(detail_url)
                bu_id = re.search("BUILDING_ID=(.*?)'",detail_res.text).group(1)
                bu.bu_id = bu_id
                bu.insert_db()
            except Exception as e:
                log.error("{}楼栋页面解析失败{}".format(url,e))
                continue
            self.house_parse(bu_id)

    def house_parse(self,bu_id):
        logic_url = 'http://www.hyfc365.com/WebRecordManager/HouseTableControl/GetData.aspx?Building_ID='+bu_id
        try:
            res = requests.get(logic_url)
            logic_id = re.search('<LOGICBUILDING_ID>(.*?)<',res.text).group(1)
            house_url = 'http://www.hyfc365.com/WebRecordManager/HouseTableControl/GetData.aspx?LogicBuilding_ID='+logic_id
            ho_res = requests.get(house_url)
            html = etree.HTML(ho_res.text)
            house_list = html.xpath("//t_house")
            for i in house_list:
                ho = House(co_index)
                ho.bu_id = bu_id
                ho.ho_name = i.xpath('./room_number/text()')[0]
                ho.ho_build_size = i.xpath('./build_area/text()')[0]
                ho.ho_share_size = i.xpath('./build_area_share/text()')[0]
                ho.ho_true_size = i.xpath('./build_area_inside/text()')[0]
                ho.ho_floor = i.xpath('./floor_realright/text()')[0]
                ho.insert_db()
        except Exception as e:
            log.error("{}房屋解析失败{}".format(logic_url,e))




