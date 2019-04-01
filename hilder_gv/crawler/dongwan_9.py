"""
url = http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/ProjectInfo.aspx?new=1
city : 东莞
CO_INDEX : 9
author: 吕三利
小区数量 : 60    2018/2/24

"""
from backup.crawler_base import Crawler
from lxml import etree
from backup.comm_info import Building, House
import requests, re
from backup.tool import Tool

co_index = 9


class Dongwan(Crawler):
    def __init__(self):
        self.url = 'http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/ProjectInfo.aspx?new=1'
        self.link_url = 'http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/'
        self.co_index = 9
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        }
        self.area_list = ['东莞市莞城区',
                          '东莞市东城区',
                          '东莞市万江区',
                          '东莞市南城区',
                          '东莞市石龙镇',
                          '东莞市虎门镇',
                          '东莞市中堂镇',
                          '东莞市望牛墩镇',
                          '东莞市麻涌镇',
                          '东莞市石碣镇',
                          '东莞市高埗镇',
                          '东莞市道滘镇',
                          '东莞市洪梅镇',
                          '东莞市长安镇',
                          '东莞市沙田镇',
                          '东莞市厚街镇',
                          '东莞市松山湖',
                          '东莞市寮步镇',
                          '东莞市大岭山镇',
                          '东莞市大朗镇',
                          '东莞市黄江镇',
                          '东莞市樟木头镇',
                          '东莞市凤岗镇',
                          '东莞市塘厦镇',
                          '东莞市谢岗镇',
                          '东莞市清溪镇',
                          '东莞市常平镇',
                          '东莞市桥头镇',
                          '东莞市横沥镇',
                          '东莞市东坑镇',
                          '东莞市企石镇',
                          '东莞市石排镇',
                          '东莞市茶山镇',
                          '东莞市虎门港',
                          '东莞市生态产业园',
                          ]

    def start_crawler(self):
        town_list = self.get_town_name()
        print(town_list)
        view_dict = Tool.get_view_state(self.url,
                                        view_state='//*[@id="__VIEWSTATE"]/@value',
                                        event_validation='//*[@id="__EVENTVALIDATION"]/@value')
        # print(view_dict)
        # print(town_list)
        all_building_url_list = self.get_all_first_page_url(town_list, view_dict)
        print(all_building_url_list)

        house_url_list = self.get_build_detail(all_building_url_list)

        self.get_house_detail(house_url_list)

    def get_house_detail(self, house_url_list):
        print(house_url_list)
        for i in house_url_list:
            try:
                response = requests.get(i, headers=self.headers)
                html = response.text
                house_html = re.search('id=.roomTable.*?id="remarkDiv"', html, re.S | re.M).group()
                house_info_list = re.findall('<td class=.*?title.*?</td>', house_html, re.S | re.M)
                bu_id = re.search('roomTable.aspx\?id=(.*?)&', html, re.S | re.M).group(1)
                for i in house_info_list:
                    house = House(co_index)
                    house.bu_id = bu_id
                    house.ho_build_size = re.search('建筑面积：(.*?) ', i, re.S | re.M).group(1)
                    house.info = re.search("(建筑面积：.*?)'>", i, re.S | re.M).group(1)
                    house.ho_name = re.search("<td.*?>(.*?)</td>", i, re.S | re.M).group(1)
                    if 'id' in house.ho_name:
                        house.ho_name = re.search('<a.*?>(.*?)</a>', house.ho_name, re.S | re.M).group(1)
                    house.insert_db()

            except Exception as e:
                print('房号错误，co_index={},url={}'.format(co_index, i), e)
        print('房号放入完成')

    def get_build_detail(self, all_building_url_list):
        house_url_list = []
        for i in all_building_url_list:
            try:
                response = requests.get(i, headers=self.headers)
                html = response.text
                tree = etree.HTML(html)
                bo_develops = tree.xpath('//*[@id="content_1"]/div[3]/text()[2]')[0]  # 开发商
                bu_build_size = tree.xpath('//*[@id="houseTable_1"]/tr[2]/td[6]/a/text()')  # 销售面积
                if bu_build_size:
                    bu_build_size = bu_build_size[0]
                bu_pre_sale = tree.xpath('//*[@id="houseTable_1"]/tr[2]/td[1]/a/text()')  # 预售证书
                if bu_pre_sale:
                    bu_pre_sale = bu_pre_sale[0]
                bu_floor = tree.xpath('//*[@id="houseTable_1"]/tr[2]/td[3]/a/text()')[0]  # 总层数
                bu_all_house = tree.xpath('//*[@id="houseTable_1"]/tr[2]/td[4]/a/text()')[0]  # 总套数
                bu_type = tree.xpath('//*[@id="houseTable_1"]/tr[2]/td[5]/a/text()')[0]  # 房屋用途
                build_html = re.search('houseTable_1.*?当前共有', html, re.S | re.M).group()
                build_detail_html = re.findall('class.*?</a></td>.*?</a></td>.*?</a></td>', build_html, re.S | re.M)
                bu_num = re.findall('项目名称：</b>(.*?)</div>', html, re.S | re.M)[0].strip()
                url_list = []
                for bu in build_detail_html:
                    try:
                        build = Building(co_index)
                        build.bu_id = re.search("href='roomTable.aspx\?id=(.*?)&", bu, re.S | re.M).group(1)
                        build.bu_address = re.search("_blank.*?_blank'>(.*?)</a></td><td>", bu, re.S | re.M).group(
                            1).strip()
                        build.bo_develops = bo_develops
                        build.bu_build_size = bu_build_size
                        build.bu_pre_sale = bu_pre_sale
                        build.bu_num = bu_num
                        build.bu_floor = bu_floor
                        build.bu_all_house = bu_all_house
                        build.bu_type = bu_type
                        for k in self.area_list:
                            if k in build.bu_address:
                                build.area = k
                                continue
                        build.insert_db()
                        house_url = re.search("(roomTable.aspx\?id=.*?&vc=.*?)'", bu, re.S | re.M).group(1)
                        url_list.append('http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/' + house_url)
                    except Exception as e:
                        print('楼栋错误，co_index={},url={}'.format(co_index, i), e)
                house_url_list = url_list + house_url_list
            except Exception as e:
                print('楼栋错误，co_index={},url={}'.format(co_index, i), e)
        return house_url_list

    @staticmethod
    def get_all_first_page_url(town_list, view_dict):
        all_building_url_list = []
        for i in town_list:
            try:
                data = {
                    'townName': i,
                    '__EVENTVALIDATION': view_dict['__EVENTVALIDATION'],
                    '__VIEWSTATE': view_dict['__VIEWSTATE'],
                }
                res = requests.post('http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/ProjectInfo.aspx?new=1', data=data)
                html = etree.HTML(res.content.decode())
                url_list = html.xpath('//*[@id="resultTable"]/tr/td[1]/a/@href')
                complete_url_list = []
                for k in url_list:
                    complete_url_list.append('http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/' + k)
                all_building_url_list = all_building_url_list + complete_url_list
            except Exception as e:
                print(e)
                continue
        return all_building_url_list

    def get_town_name(self):
        res = requests.get(self.url)
        html = etree.HTML(res.content)
        return html.xpath('//*[@id="townName"]/option/@value')
