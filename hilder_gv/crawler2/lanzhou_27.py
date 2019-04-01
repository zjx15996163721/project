"""
业务及其复杂
"""

"""
url = http://www.lzfc.com.cn:8080/LFGIS/buildingTb/webSupportAction!comHouseProList.action?pageNo=1&pageSize=1000
city : 兰州
CO_INDEX : 27
小区数量：639
"""
import requests
from lxml import etree
from backup.comm_info import Comm, Building
from backup.producer import ProducerListUrl

url = 'http://www.lzfc.com.cn:8080/LFGIS/buildingTb/webSupportAction!comHouseProList.action?pageNo=1&pageSize=1000'
co_index = '27'
city = '兰州'


class Lanzhou(object):
    def start_crawler(self):
        response = requests.get(url)
        html = response.text
        tree = etree.HTML(html)
        all_url = tree.xpath('//a[@class="a_name"]/@href')
        for i in all_url:
            comm = Comm(co_index)
            if i == '#':
                continue
            comm_url = 'http://www.lzfc.com.cn:8080' + i
            comm.co_name = "cc0.innerHTML='(.*?)'"
            comm.co_address = "cc1.innerHTML='(.*?)'"
            comm.area = "cc2.innerHTML='(.*?)'"
            comm.co_use = "cc4.innerHTML='(.*?)'"
            comm.co_develops = "cc5.innerHTML='(.*?)'"
            comm.co_open_time = "cc6.innerHTML='(.*?)'"
            comm.co_all_house = "cc9.innerHTML='(.*?)'"
            comm.co_build_size = "cc11.innerHTML='(.*?)'"
            comm.co_name = "cc0.innerHTML='(.*?)'"
            comm.co_id = "BaseCode=(.*?)'"
            p = ProducerListUrl(page_url=comm_url,
                                request_type='get', encode='gbk',
                                analyzer_rules_dict=comm.to_dict(),
                                current_url_rule="queryBuildHerf1.href='(.*?)'",
                                analyzer_type='regex')
            build_url = p.get_details()
            for i in build_url:
                build = Building(co_index)
                build_detail_url = 'http://www.lzfc.com.cn:8080' + i
                build.bu_num = 'onclick=comInfoView.*?center">(.*?)<'
                build.co_use = 'onclick=comInfoView.*?center.*?center">(.*?)<'
                build.bu_pre_sale = 'onclick=comInfoView.*?center.*?center.*?center"><.*?>(.*?)<'
                build.bu_all_house = 'onclick=comInfoView.*?center.*?center.*?center.*?center">(.*?)<'
                build.co_name = 'fontbg_red">(.*?)<'
                build.bu_id = "onclick=comInfoView\('(.*?)'\)"
                p = ProducerListUrl(page_url=comm_url,
                                    request_type='get', encode='gbk',
                                    analyzer_rules_dict=comm.to_dict(),
                                    current_url_rule="queryBuildHerf1.href='(.*?)'",
                                    analyzer_type='regex')
                build_url = p.get_details()


if __name__ == '__main__':
    lan = Lanzhou()
    lan.start_crawler()
