"""
url = http://www.tmsf.com/newhouse/property_searchall.htm
city：杭州
CO_INDEX: 15
小区数：2066
"""
from retry import retry
from backup.crawler_base import Crawler
from backup.comm_info import Comm, Building, House
from backup.get_page_num import AllListUrl
from backup.producer import ProducerListUrl
import requests, re

url = 'http://www.tmsf.com/newhouse/property_searchall.htm'
co_index = '15'
city = '杭州'

count = 0


class Hangzhou(Crawler):
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
                       page_count_rule='green1">1/(.*?)<',
                       )
        page = b.get_page_count()
        for i in range(1, int(page) + 1):
            all_url = 'http://www.tmsf.com/newhouse/property_searchall.htm?&page=' + str(i)
            while True:
                try:
                    response = requests.get(all_url, headers=self.headers, timeout=10)
                    if response.status_code is 200:
                        break
                except Exception as e:
                    print('小区列表页加载不出来,co_index={},url={}'.format(co_index, all_url), e)
            html = response.text
            comm_url_list = re.findall('build_word01" onclick="toPropertyInfo\((.*?)\);', html, re.S | re.M)
            self.get_comm_info(comm_url_list)

    @retry(tries=3)
    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            try:
                code = i.split(',')
                comm_url = 'http://www.tmsf.com/newhouse/property_' + code[0] + '_' + code[1] + '_info.htm'
                comm = Comm(co_index)
                comm.co_name = 'buidname.*?>(.*?)<'
                comm.co_address = '--位置行--.*?<span.*?title="(.*?)"'
                comm.co_build_type = '建筑形式：<.*?>(.*?)<'
                comm.co_develops = '项目公司：<.*?>(.*?)<'
                comm.co_volumetric = '容 积 率：</span>(.*?)<'
                comm.co_green = '绿 化 率：</span>(.*?)<'
                comm.co_size = '占地面积：</span>(.*?)<'
                comm.co_build_size = '总建筑面积：</span>(.*?)<'
                comm.co_all_house = '总户数：</span>(.*?)<'
                comm.co_id = 'info" href="/newhouse/property_(.*?)_info'
                p = ProducerListUrl(page_url=comm_url,
                                    request_type='get', encode='utf-8',
                                    analyzer_rules_dict=comm.to_dict(),
                                    current_url_rule='一房一价<.*?href="(.*?)"',
                                    analyzer_type='regex',
                                    headers=self.headers)
                build_all_url = p.get_details()
                global count
                count += 1
                print('comm:', count)
                self.get_build_info(build_all_url)
            except Exception as e:
                print('小区页面,co_index={},url={}'.format(co_index, comm_url), e)

    @retry(tries=3)
    def get_build_info(self, build_all_url):
        build_url = 'http://www.tmsf.com/' + build_all_url[0]
        try:
            response = requests.get(build_url, headers=self.headers)
        except Exception as e:
            print('楼栋错误,co_index={},url={}'.format(co_index, build_url), e)
            return
        html = response.text
        build_code_list = re.findall("javascript:doPresell\('(.*?)'\)", html)
        sid = re.findall('id="sid" value="(.*?)"', html)[0]
        propertyid = re.findall('id="propertyid" value="(.*?)"', html)[0]
        co_id = sid + '_' + propertyid
        for presellid in build_code_list:
            build_detail_url = build_url + '?presellid=' + presellid
            try:
                result = requests.get(build_detail_url, headers=self.headers, timeout=10).text
            except Exception as e:
                print("楼栋错误,co_index={},url={}".format(co_index, build_detail_url), e)
                continue
            build_num_html = re.search("幢　　号.*?面　　积：", result, re.S | re.M).group()
            build_num_list = re.findall('<a.*?</a>', build_num_html, re.S | re.M)
            for i in build_num_list:
                build = Building(co_index)
                build_num = re.search("doBuilding\('(.*?)'\)", i, re.S | re.M).group(1)
                build.bu_num = re.search("doBuilding.*?>(.*?)<", i, re.S | re.M).group(1)
                build.bu_id = build_num
                build.co_id = co_id
                build.insert_db()
                self.get_house_info(build_num, sid)

    @retry(tries=3)
    def get_house_info(self, build_num, sid):
        try:
            house_url = 'http://www.tmsf.com/newhouse/NewPropertyHz_showbox.jspx?buildingid=' + build_num + '&sid=' + sid
            house = House(co_index)
            house.bu_id = 'buildingid":(.*?),'
            house.co_build_size = 'builtuparea":(.*?),'
            house.ho_price = 'declarationofroughprice":(.*?),'
            house.ho_name = 'houseno":(.*?),'
            house.ho_true_size = 'setinsidefloorarea":(.*?),'
            house.ho_share_size = 'poolconstructionarea":(.*?),'
            house.ho_type = 'houseusage":(.*?),'
            p_2 = ProducerListUrl(page_url=house_url,
                                  request_type='get', encode='utf-8',
                                  analyzer_rules_dict=house.to_dict(),
                                  analyzer_type='regex',
                                  headers=self.headers)
            p_2.get_details()
        except Exception as e:
            print('房号错误,co_index={},url={}'.format(co_index, house_url), e)


if __name__ == '__main__':
    b = Hangzhou()
    b.start_crawler()
