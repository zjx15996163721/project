"""
url: http://61.178.148.157:8081/bit-xxzs/xmlpzs/nowwebissue.asp
city: 本溪，呼和浩特，景德镇，临沂，渭南，西宁，许昌，白银，宝鸡，
author: 吕三利
"""
import requests
from lxml import etree
import re
from backup.comm_info import Comm, Building, House
from backup.crawler_base import Crawler
from retry import retry


class AllInOne(Crawler):
    def __init__(self, url, url_front, co_index):
        self.url = url
        self.URL_FRONT = url_front
        self.CO_INDEX = co_index

    @retry(tries=3)
    def get_all_page(self):
        try:
            res = requests.get(url=self.url)
            html = res.content.decode('gbk').replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '')
            page = re.search(r'共有(.*?)页', html).group(1)
            print(page)
            return page
        except Exception as e:
            print(e)
            raise

    @retry(tries=3)
    def baiyin_start(self):
        page = self.get_all_page()
        print(page)
        for i in range(1, int(page) + 1):
            res = requests.get(self.url + '?page=' + str(i))
            html = res.content.decode('gbk')
            tree = etree.HTML(html)
            community_list = tree.xpath('//tr[@align="center"]')
            for i in community_list[1:]:
                try:
                    comm = Comm(self.CO_INDEX)
                    href = i.xpath('td/a/@href')
                    area = i.xpath('td[1]/text()')
                    if not area:
                        area = None
                    else:
                        area = area[0]
                    href = href[0]
                    comm.area = area
                    self.get_comm_detail(href, comm)
                except Exception as e:
                    href = i.xpath('td/a/@href')
                    if not href:
                        continue
                    href = href[0]
                    comm_url = self.URL_FRONT + href
                    print('小区错误：', comm_url)
                    print(e)

    @staticmethod
    def regex_common(regex, html):
        """
        正则表达式
        若果有返回结果结果
        没有
        :param regex: 正则表达式
        :param html: 需要匹配的网页
        :return:
        """
        if re.findall(regex, html, re.M | re.S):
            result = re.findall(regex, html, re.M | re.S)
            return result[0]
        else:
            return None

    @retry(tries=3)
    def get_comm_detail(self, href, comm):
        comm_detail_url = self.URL_FRONT + href
        response = requests.get(url=comm_detail_url)
        co_id = response.url
        co_id = int(co_id.split('=')[1])  # 小区id
        html = response.content.decode('gbk')

        co_name = self.regex_common(r'项目名称.*?<td.*?>(.*?)</td>', html)  # 小区名字
        co_owner = self.regex_common(r'房屋所有权证号.*?<td.*?>(.*?)</td>', html)
        co_use = self.regex_common(r'用　　途.*?<td.*?>(.*?)</td>', html)
        co_develops = self.regex_common(r'开 发 商.*?<td.*?>(.*?)</td>', html)
        co_address = self.regex_common(r'项目位置.*?<td.*?>(.*?)</td>', html)
        co_pre_sale = self.regex_common(r'预售证号.*?<td.*?>(.*?)</td>', html)
        co_land_use = self.regex_common(r'土地使用权证.*?<td.*?>(.*?)</td>', html)
        co_land_type = self.regex_common(r'土地权证类型.*?<td.*?>(.*?)</td>', html)
        co_handed_time = self.regex_common(r'终止日期.*?<td.*?>(.*?)</td>', html)
        co_plan_pro = self.regex_common(r'规划许可证.*?<td.*?>(.*?)</td>', html)
        co_work_pro = self.regex_common(r'施工许可证.*?<td.*?>(.*?)</td>', html)
        co_type = self.regex_common(r'项目类型.*?<td.*?>(.*?)</td>', html)  # 小区类型
        co_size = self.regex_common(r'批准面积.*?<td.*?>(.*?)</td>', html)  # 占地面积
        comm.co_id = co_id
        comm.co_name = co_name
        comm.co_type = co_type
        comm.co_size = co_size
        comm.co_owner = co_owner
        comm.co_use = co_use
        comm.co_develops = co_develops
        comm.co_address = co_address
        comm.co_pre_sale = co_pre_sale
        comm.co_land_use = co_land_use
        comm.co_land_type = co_land_type
        comm.co_handed_time = co_handed_time
        comm.co_plan_pro = co_plan_pro
        comm.co_work_pro = co_work_pro
        # 获取楼栋url列表
        build_url_list = re.findall(r"<td><a href='(.*?)'", html, re.M | re.S)
        if not build_url_list:
            return
        else:
            for build_url in build_url_list:
                try:
                    building = Building(self.CO_INDEX)
                    build_id = re.search(r'<td>(\d{2,6})</td>', html, re.M | re.S).group(1)  # 楼栋id
                    bu_all_house = re.search(r'<td>(\d{1,3})</td>', html, re.M | re.S).group(1)  # 总套数
                    bu_price_demo = re.findall('<td>[\.\d]+</td>', html, re.M | re.S)[4]
                    bu_price = re.search('\d+', bu_price_demo).group()
                    data_dict = self.get_build_detail(build_url)
                    bu_num = data_dict['bu_num']  # 楼号
                    bu_build_size = data_dict['bu_build_size']  # 建筑面积
                    bu_address = data_dict['co_address']
                    co_build_end_time = data_dict['co_build_end_time']  # 竣工时间
                    co_build_type = data_dict['co_build_type']  # 竣工时间
                    if not co_build_end_time:
                        building.co_is_build = '1'
                    comm.co_build_end_time = co_build_end_time
                    comm.bu_build_size = bu_build_size
                    comm.co_build_type = co_build_type
                    # 楼栋
                    building.bu_address = bu_address
                    building.bu_num = bu_num
                    building.bu_build_size = bu_build_size
                    building.bu_all_house = bu_all_house
                    building.bu_id = build_id
                    building.co_id = co_id
                    building.bu_price = bu_price
                    # 插入
                    building.insert_db()
                    house_url = re.search(r'href="/(tt/business/buildingRooms_view.*?)"', html, re.M | re.S).group(1)
                    self.get_house_info(house_url, build_id, co_id)
                except Exception as e:
                    build_detail_url = self.URL_FRONT + build_url
                    print('楼栋错误：', build_detail_url)
        comm.insert_db()

    def get_house_info(self, house_url, build_id, co_id):
        ho_url = self.URL_FRONT.replace('bit-xxzs/xmlpzs/', '') + house_url
        response = requests.get(ho_url)
        html = response.content.decode('gbk')
        row_max = len(re.findall("点击可选中该行所有房屋！'>(.*?)<", html, re.S | re.M))
        col_max = int(re.findall("层房序号：(\d+)'", html, re.S | re.M)[-1].strip())
        info_list = re.findall("title='点击可选中该行所有房屋！' >.*?\[(.*?)\]", html, re.S | re.M)
        for row in range(1, row_max + 1):
            all_house = info_list[row-1].split('/')[0]
            build_size = info_list[row-1].split('/')[1]
            for col in range(1, col_max + 1):
                house = House(co_index=self.CO_INDEX)
                if col >= 10:
                    ho_name = str(row) + str(col)
                else:
                    ho_name = str(row) + '0' + str(col)
                house.ho_name = ho_name
                house.all_house = all_house
                house.build_size = build_size
                house.bu_id = build_id
                house.co_id = co_id
                house.insert_db()

    @retry(tries=3)
    def get_build_detail(self, build_url):
        build_detail_url = self.URL_FRONT + build_url
        response = requests.get(url=build_detail_url)
        html = response.content.decode('gbk').replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '')
        bu_num = re.search('销售楼号(.*?)<td>(.*?)</td>', html, re.M | re.S).group(2)  # 楼号
        bu_build_size = re.search('建筑面积(.*?)<td>(.*?)</td>', html, re.M | re.S).group(2)  # 建筑面积
        co_address = re.search('楼盘座落(.*?)<td>(.*?)</td>', html, re.M | re.S).group(2)  # 小区地址
        co_build_end_time = re.search('完工日期(.*?)<td>(.*?)</td>', html, re.M | re.S).group(2)  # 竣工时间
        co_build_type = re.search('楼盘结构(.*?)<td>(.*?)</td>', html, re.M | re.S).group(2)  # 建筑结构
        data_dict = {}
        data_dict['bu_num'] = bu_num
        data_dict['bu_build_size'] = bu_build_size
        data_dict['co_address'] = co_address
        data_dict['co_build_end_time'] = co_build_end_time
        data_dict['co_build_type'] = co_build_type
        return data_dict

    def start_crawler(self):
        self.baiyin_start()


if __name__ == '__main__':
    sp_list_no_p = [
        # 本溪
        {'url': 'http://gs.bxfdc.cn/xmlpzs/webissue.asp?',
         'url_front': 'http://gs.bxfdc.cn/xmlpzs/', 'co_index': '1025', },
        # 呼和浩特
        {'url': 'http://60.31.254.197/bit-xxzs/xmlpzs/webissue.asp',
         'url_front': 'http://60.31.254.197/bit-xxzs/xmlpzs/', 'co_index': '1027', },
        # 景德镇
        {'url': 'http://www.jdzfgj.cn/bit-xxzs/xmlpzs/nowwebissue.asp',
         'url_front': 'http://www.jdzfgj.cn/bit-xxzs/xmlpzs/', 'co_index': '1028', },
        # 临沂
        {'url': 'http://lyfdc.gov.cn:88/bit-xxzs/xmlpzs/webissue.asp?',
         'url_front': 'http://lyfdc.gov.cn:88/bit-xxzs/xmlpzs/', 'co_index': '1030', },
        # 渭南
        {'url': 'http://www.wnfdc.com/bit-xxzs/xmlpzs/webissue.asp',
         'url_front': 'http://www.wnfdc.com/bit-xxzs/xmlpzs/', 'co_index': '1031', },
        # 西宁
        {'url': 'http://www.xnfcxx.com/bit-xxzs/xmlpzs/webissue.asp',
         'url_front': 'http://www.xnfcxx.com/bit-xxzs/xmlpzs/', 'co_index': '1032', },
        # 许昌
        {'url': 'http://222.89.166.137/bit-xxzs/xmlpzs/webissue.asp',
         'url_front': 'http://222.89.166.137/bit-xxzs/xmlpzs/', 'co_index': '1033', },
        # 白银
        {'url': 'http://61.178.148.157:8081/bit-xxzs/xmlpzs/nowwebissue.asp',
         'url_front': 'http://61.178.148.157:8081/bit-xxzs/xmlpzs/', 'co_index': '0', },
        # 宝鸡
        {'url': 'http://61.185.69.154/bit-xxzs/xmlpzs/webissue.asp?',
         'url_front': 'http://61.185.69.154/bit-xxzs/xmlpzs/', 'co_index': '1024'},
        # 东营
        {'url': 'http://www.dyfc.gov.cn/bit-xxzs/xmlpzs/nowwebissue.asp?',
         'url_front': 'http://www.dyfc.gov.cn/bit-xxzs/xmlpzs/', 'co_index': '1026', },
        # 庆阳
        {'url': 'http://60.165.104.70/bit-xxzs/xmlpzs/webissue.asp',
         'url_front': 'http://60.165.104.70/bit-xxzs/xmlpzs/', 'co_index': '155', },
    ]

    # for i in sp_list_no_p:
    #     baiyin = AllInOne(url=i['url'], url_front=i['url_front'], co_index=i['co_index'], )
    #     baiyin.start_crawler()
