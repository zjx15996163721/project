"""
url = http://www.gzbjfc.com/House.aspx
city : 毕节
CO_INDEX : 3
小区数量：
"""
import re
import requests

from backup.comm_info import Comm, Building, House
from backup.crawler_base import Crawler
from backup.get_page_num import AllListUrl
from backup.producer import ProducerListUrl

url = 'http://www.gzbjfc.com/House.aspx'
co_index = '3'
city = '毕节'


class Bijie(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        b = AllListUrl(first_page_url=url,
                       request_method='get',
                       analyzer_type='regex',
                       encode='utf-8',
                       page_count_rule='下页</a>.*?page=(.*?)"',
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            try:
                all_page_url = url + '?page=' + str(i)
                response = requests.get(all_page_url, headers=self.headers)
                html = response.text
                comm_url_list = re.findall('项目名称：.*?href="(.*?)"', html, re.S | re.M)
                self.get_comm_info(comm_url_list)
            except Exception as e:
                print('page页面错误,co_index={},url={}'.format(co_index, all_page_url), e)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                comm = Comm(co_index)
                comm_url = 'http://www.gzbjfc.com/' + i
                comm.co_name = 'cph_hif1_xmmc.*?<.*?>(.*?)<'
                comm.co_pre_sale = 'cph_hif1_xsxkz.*?<.*?>(.*?)<'
                comm.co_address = 'cph_hif1_zl.*?<.*?>(.*?)<'
                comm.co_develops = 'cph_hif1_kfs.*?<.*?>(.*?)<'
                comm.co_handed_time = 'cph_hif1_jfsj.*?<.*?>(.*?)<'
                comm.co_build_size = 'cph_hif1_jzmj.*?>(.*?)<'
                comm.co_all_house = 'cph_hif1_fwts.*?>(.*?)<'
                comm.co_id = 'hdl1_hfYszh" value="(.*?)"'
                p = ProducerListUrl(page_url=comm_url,
                                    request_type='get', encode='utf-8',
                                    analyzer_rules_dict=comm.to_dict(),
                                    analyzer_type='regex',
                                    headers=self.headers)
                p.get_details()
                # 楼栋信息
                build_url = comm_url.replace('Info', 'Building')
                self.get_build_info(build_url)
            except Exception as e:
                print('小区错误,co_index={},url={}'.format(co_index, comm_url), e)

    def get_build_info(self, build_url):
        try:
            build = Building(co_index)
            response = requests.get(build_url, headers=self.headers)
            'http://www.gzbjfc.com/House/Table.aspx?xmmc=%E5%85%B0%E6%A1%A5%E5%9C%A3%E8%8F%B2&yszh=bj1740&qu=%E6%AF%95%E8%8A%82&zhlx=xs&dongID=30012124'
            html = response.text
            bu_id_list = re.findall('cph_hb1_dg1.*?center.*?center.*?<td>(.*?)<', html, re.S | re.M)
            build.co_id = re.findall('hdl1_hfYszh" value="(.*?)"', html, re.S | re.M)[0]
            build.bu_num = self.get_build_num(build.co_id)
            bu_all_house_list = re.findall('cph_hb1_dg1.*?center.*?center.*?<td>.*?<td>.*?<td>(.*?)<', html,
                                           re.S | re.M)
            house_url_list = re.findall('cph_hb1_dg1.*?<a.*?href="(.*?)"', html,
                                        re.S | re.M)
            for i in range(len(bu_id_list)):
                build.bu_id = bu_id_list[i]
                build.bu_all_house = bu_all_house_list[i]
                build.insert_db()
            self.get_house_info(house_url_list)
        except Exception as e:
            print('楼栋错误,co_index={},url={}'.format(co_index, build_url), e)

    def get_build_num(self, co_id):
        build_url = 'http://www.gzbjfc.com/House/Table.aspx?yszh=' + co_id + '&qu=%E6%AF%95%E8%8A%82&zhlx=xs'
        res = requests.get(build_url, headers=self.headers)
        html = res.text
        build_num = re.findall('selected="selected" value=".*?>.*? (.*?)<', html, re.S | re.M)[0]
        return build_num

    def get_house_info(self, house_url_list):
        for i in house_url_list:
            try:
                dong_ID = re.search('dongID=(.*?)$', i).group(1)
                yszh = re.search('yszh=(.*?)&', i).group(1)
                house_url = 'http://www.gzbjfc.com/Controls/HouseControls/FloorView.aspx?dongID=' + dong_ID + '&qu=%E6%AF%95%E8%8A%82&yszh=' + yszh + '&zhlx=xs&danyuan=all'
                response = requests.get(house_url, headers=self.headers)
                html = response.text
                bu_id = re.findall('dongID=(.*?)&', html, re.S | re.M)[0]
                info_str = re.search('<div class="HouseFloorView".*', html, re.S | re.M).group()
                for k in re.findall('<div class.*?</table></div>', info_str, re.S | re.M):
                    house = House(co_index)
                    if '层' in k:
                        continue
                    if '单元' in k:
                        continue
                    print(k)
                    house.info = k
                    house.ho_name = re.search('span.*?>(.*?)</span>', k, re.S | re.M).group(1)
                    house.ho_true_size = re.search('title.*\n(.*?)\n', k).group(1)
                    house.bu_id = bu_id
                    house.insert_db()

                # ho_name_list = re.findall('<span.*?>(.*?)<', html, re.S | re.M)
                # info_list = re.findall("<div class=.*?title='(.*?)'.*?<span", html, re.S | re.M)
                # for i in range(len(ho_name_list)):
                #     house = House(co_index)
                #     house.bu_id = bu_id
                #     house.ho_name = ho_name_list[i]
                #     house.info = info_list[i]
                #     house.insert_db()
            except Exception as e:
                print('房号错误,co_index={},url={}'.format(co_index, house_url), e)
