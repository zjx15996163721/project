"""
url = http://www.bsfcj.com/PubInfo/HouseSource.asp?page=1&xm_xzqy=&xm_xmmc=&xm_xmdz=&xm_kfs=&xm_fwhx=
city: 百色
CO_INDEX: 1
author: 周彤云
小区数：99
time:2018-02-11
"""

import requests
from lxml import etree
from backup.comm_info import Comm, Building, House
from backup.crawler_base import Crawler
import re


class Baise(Crawler):
    url = 'http://www.bsfcj.com/PubInfo/HouseSource.asp'
    co_index = 1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
    }

    def get_all_page_url(self):
        try:
            res = requests.get(url=self.url, headers=self.headers)
            first_page_html = res.content.decode('gb2312')
            page_count = re.search('/(\d+)</strong>页', first_page_html, re.S | re.M).group(1)
            print('总页数', page_count)
            url_list = []
            for i in range(1, int(page_count) + 1):
                url_list.append(self.url + '?page=' + str(i))
            return url_list
        except Exception as e:
            print('获取所有页面错误, co_index, url={}'.format(self.co_index, self.url), e)

    def start_crawler(self):
        url_list = self.get_all_page_url()
        for url in url_list:
            res = requests.get(url, headers=self.headers)
            html = res.content.decode('gb2312')
            info_list = re.search('可售套数(.*?)<!--进行翻页显示和处理-->', html, re.S | re.M).group(1)
            for info in re.findall('<tr.*?</tr>', info_list, re.S | re.M):
                try:
                    comm = Comm(1)

                    comm_detail_url = re.search('<a href="(.*?)">', info, re.S | re.M).group(1)
                    comm_area = re.findall('<td align="center">(.*?)</td>', info, re.S | re.M)[1]
                    comm.area = comm_area
                    # href = 'http://www.bsfcj.com/PubInfo/' + 'lpxx.asp?qyxmbm=DBDHDADCDADADADFDDDBDCDJ000001'
                    href = 'http://www.bsfcj.com/PubInfo/' + comm_detail_url

                    comm = self.get_comm_detail(href, comm)
                    comm.insert_db()
                except Exception as e:
                    print('小区列表页解析有错,co_index={},'.format(self.co_index), e)

    def get_comm_detail(self, href, comm):
        try:
            res = requests.get(url=href, headers=self.headers)
            co_id = res.url.split('=')[1]  # 小区id
            html = res.content.decode('gb2312')
            # 获取小区详情字段
            co_name = re.search('项目名称：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 小区名
            co_address = re.search('项目地址：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 地址
            co_investor = re.search('投资商：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 投资商
            co_is_build = re.search('是否在建：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 是否在建
            co_type = re.search('项目类型：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 项目类型
            co_size = re.search('占地面积：.*?padingleft3px">(.*?)<', html, re.S | re.M).group(1)  # 占地面积
            co_build_size = re.search('建筑面积：.*?padingleft3px">(.*?)<', html, re.S | re.M).group(1)  # 建筑面积
            co_build_start_time = re.search('开工日期（计划）：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 开工时间
            co_build_end_time = re.search('竣工日期（计划）：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 竣工时间
            co_volumetric = re.search('容积率：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 容积率
            co_green = re.search('绿化率：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 绿化率
            # 预售证书为列表
            co_pre_sale_list_str = re.search('预\(现\)售许可证：.*?height:25px;"(.*?)</td>', html, re.S | re.M).group(
                1)  # 预售证书
            co_pre_sale = []
            for i in re.findall('>(.*?)<', co_pre_sale_list_str, re.S | re.M):
                co_pre_sale.append(i)
            # 预售证书时间也是列表
            co_pre_sale_data_list_str = re.search('预\(现\)售许可证发证日期：.*?height:25px;"(.*?)</td>', html, re.S | re.M).group(
                1)  # 预售证书日期
            co_pre_sale_date = []
            for i in re.findall('>(.*?)<', co_pre_sale_data_list_str, re.S | re.M):
                co_pre_sale_date.append(i)

            co_land_use = re.search('土地使用权证：.*?padingleft3px">(.*?)</td>', html, re.S | re.M).group(1)  # 土地使用证

            comm.co_id = co_id
            comm.co_name = co_name
            comm.co_address = co_address
            comm.co_investor = co_investor
            comm.co_is_build = co_is_build
            comm.co_type = co_type
            comm.co_size = co_size
            comm.co_build_size = co_build_size
            comm.co_build_start_time = co_build_start_time
            comm.co_build_end_time = co_build_end_time
            comm.co_volumetric = co_volumetric
            comm.co_green = co_green
            comm.co_pre_sale = co_pre_sale
            comm.co_land_use = co_land_use
            comm.co_pre_sale_date = co_pre_sale_date
            # 获取楼栋超链接
            res = requests.get(url=href, headers=self.headers)
            html = res.content.decode('gb2312', 'ignore')
            tree = etree.HTML(html)
            build_url_list = tree.xpath('//tr[@bgcolor="#FFFFFF"]/td[7]')
            if not build_url_list:
                return comm
            else:
                for i in build_url_list:
                    build_url = i.xpath('p/a/@href')[0]
                    building_url = 'http://www.bsfcj.com/PubInfo/' + build_url
                    building = Building(1)
                    building_obj = self.get_build_detail(building_url, building, co_id, )
                    building_obj.insert_db()
                return comm
        except Exception as e:
            print('小区页面解析错误，co_index={},url={}'.format(self.co_index, href), e)

    def get_build_detail(self, building_url, building, co_id):
        try:
            res = requests.get(url=building_url, headers=self.headers)
            html = res.content.decode('gb2312', 'ignore').replace('\n', '').replace('\r', '').replace('\t', '').replace(
                ' ', '')
            bu_id = building_url.split('=')[1].split('&')[0]  # 楼栋id
            bu_name = re.search(
                r'项目名称：</td><tdwidth="1"rowspan="6"background="images/trbg3.gif"></td><tdwidth="200"align="left"class="padingleft3px">(.*)?</td><tdwidth="1"rowspan="6"align="right"bgcolor="#CECFCE"></td><tdwidth="2"rowspan="6"align="right"bgcolor="#FFFFFF">',
                html).group(1)  # 楼栋名称
            bu_num = re.search(
                r'号：</td><tdwidth="1"rowspan="6"background="images/trbg3.gif"></td><tdalign="left"class="padingleft3px">(.*)?</td></tr><tr><tdheight="25"align="right">总&nbsp;套&nbsp;数',
                html).group(1)  # 栋号
            # print(bu_num)
            bu_all_house = re.search(
                r'总&nbsp;套&nbsp;数：</td><tdalign="left"class="padingleft3px">(.*?)</td><tdalign="right">可售套数',
                html).group(1)  # 总套数
            bu_floor = re.search(r'总层数：</td><tdalign="left"class="padingleft3px">(.*)?</td><tdalign="right">项目类型',
                                 html).group(1)  # 总层数
            bu_build_size = re.search(
                r'建筑面积：</td><tdalign="left"class="padingleft3px"><FONTcolor=#ff0000>(.*)?M&sup2;</FONT></td><tdalign="right">住宅面积'
                , html).group(1)  # 建筑面积
            bu_live_size = re.search(
                r'住宅面积：</td><tdalign="left"class="padingleft3px">(.*)?M&sup2;</td></tr><tr><tdheight="25"align="right">幢套内建筑面积',
                html).group(1)  # 住宅面积
            bu_not_live_size = re.search(
                r'非住宅面积：</td><tdalign="left"class="padingleft3px">(.*)?M&sup2;</td></tr><tr><tdheight="25"align="right">预'
                , html).group(1)  # 非住宅面积
            bu_price = re.search(
                r'拟销住宅价格：</td><tdbackground="images/trbg3.gif"></td><tdalign="left"class="padingleft3px">(.*)?</td><tdalign="right"bgcolor="#CECFCE"></td><tdalign="right"bgcolor="#FFFFFF"></td><tdalign="right"bgcolor="#CECFCE"></td><tdalign="right">拟销商业门面价格'
                , html).group(1).split('元')[0]  # 住宅价格

            bu_type = re.search('项目类型：</td>.*?ft3px">(.*?)</td>', html, re.S | re.M).group(1)
            building.co_id = co_id
            building.bu_id = bu_id
            building.bu_name = bu_name
            building.bu_num = bu_num
            building.bu_all_house = bu_all_house
            building.bu_floor = bu_floor
            building.bu_build_size = bu_build_size
            building.bu_live_size = bu_live_size
            building.bu_not_live_size = bu_not_live_size
            building.bu_price = bu_price
            building.bu_type = bu_type
            # 获取房号超链接
            house_url_list = re.findall(r"window.open\('(.+?)'\)", html)
            for i in house_url_list:
                house_url = 'http://www.bsfcj.com/PubInfo/' + i
                house = House(1)
                house_obj = self.get_house_detail(house_url, house, co_id, bu_id)
                house_obj.insert_db()
            return building
        except Exception as e:
            print('楼栋解析或者请求的过程中出现错误,co_index={},url={}'.format(self.co_index, building_url), e)

    def get_house_detail(self, house_url, house, co_id, bu_id):
        try:
            res = requests.get(url=house_url, headers=self.headers)
            html = res.content.decode('gb2312', 'ignore')
            tree = etree.HTML(html)
            ho_name = tree.xpath('//td[@width="82"]/text()')[0]  # 房号
            ho_floor = tree.xpath('//td[@width="72"]/text()')[0]  # 楼层
            ho_type = tree.xpath('//tr[3]/td[@bgcolor="#FFFFEE"][2]/text()')[0]  # 房屋类型
            ho_room_type = tree.xpath('//tr[3]/td[@bgcolor="#FFFFEE"][4]/text()')[0]  # 户型
            ho_build_size = tree.xpath('//tr[4]/td[2]/text()')[0].replace('M²', '')  # 建筑面积
            ho_true_size = tree.xpath('//tr[4]/td[4]/text()')[0].replace('M²', '')  # 预测套内面积
            ho_share_size = tree.xpath('//tr[5]/td[2]/text()')[0].replace('M²', '')  # 预测分摊面积
            orientation = tree.xpath('//tr[6]/td[2]/text()')[0]  # 朝向
            ho_price = tree.xpath('//tr[6]/td[4]/text()')  # 价格

            house.co_id = co_id
            house.bu_id = bu_id
            house.ho_name = ho_name
            house.ho_floor = ho_floor
            house.ho_type = ho_type
            house.ho_room_type = ho_room_type
            house.ho_build_size = ho_build_size
            house.ho_true_size = ho_true_size
            house.ho_share_size = ho_share_size
            house.orientation = orientation
            house.ho_price = ho_price
            return house
        except Exception as e:
            print('房号请求或者解析过程之中出现问题,co_index={},url={}'.format(self.co_index, house_url), e)
