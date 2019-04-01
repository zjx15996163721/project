"""
url = http://www.jyfg.cn/HouseWebSetup/PublicReport/PublicInfoIndex.aspx
city : 揭阳
CO_INDEX : 23
小区数量：109
"""
from backup.comm_info import Comm, Building, House
import re, requests
from lxml import etree

url = 'http://www.jyfg.cn/HouseWebSetup/PublicReport/PublicInfoIndex.aspx'
co_index = '23'
city = '揭阳'


class Jieyang(object):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        }

    def start_crawler(self):
        response = requests.get(url)
        html = response.text
        tree = etree.HTML(html)
        comm_list = tree.xpath('//tr[@class="Row"]/td[1]/text()')
        co_develops_list = tree.xpath('//tr[@class="Row"]/td[3]/text()')
        co_address_list = tree.xpath('//tr[@class="Row"]/td[8]/text()')
        co_open_time_list = tree.xpath('//tr[@class="Row"]/td[9]/text()')
        co_pre_sale_list = tree.xpath('//tr[@class="Row"]/td[5]/text()')
        co_all_house_list = tree.xpath('//tr[@class="Row"]/td[11]/text()')
        co_build_size_list = tree.xpath('//tr[@class="Row"]/td[10]/text()')
        co_name_list = tree.xpath('//tr[@class="Row"]/td[4]/text()')
        for co in range(0, len(comm_list)):
            try:
                comm = Comm(co_index)
                comm_url = 'http://www.jyfg.cn/HouseWebSetup/PublicReport/PreSellLicenceDetailInfo.aspx?PreSellLicenceSN=' + \
                           comm_list[
                               co]
                result = requests.get(comm_url)
                html_build = result.text
                tree = etree.HTML(html_build)
                build_list = tree.xpath('//tr[@class="Row"]/td[1]/text()')
                area = tree.xpath('//*[@id="LabSCFW"]/text()')[0]
                comm.co_id = comm_list[co]
                comm.area = area
                comm.co_develops = co_develops_list[co]
                comm.co_address = co_address_list[co]
                comm.co_open_time = co_open_time_list[co]
                comm.co_pre_sale = co_pre_sale_list[co]
                comm.co_all_house = co_all_house_list[co]
                comm.co_build_size = co_build_size_list[co]
                comm.co_develops = co_develops_list[co]
                comm.co_name = co_name_list[co]
                comm.insert_db()
                for bu in range(0, len(build_list)):
                    try:

                        build_url = 'http://www.jyfg.cn/HouseWebSetup/PublicReport/PubRptHouseList.aspx?BuildingSN=' + \
                                    build_list[bu]
                        res = requests.get(build_url,headers=self.headers)
                        con = res.content.decode('gbk')
                        building = Building(co_index)

                        building.co_id = comm.co_id
                        building.bu_id = build_list[bu]
                        building.bu_num = re.search('栋号.*?<span.*?">(.*?)</span',con,re.S|re.M).group(1)
                        building.bu_build_size = re.search('总建筑面积.*?<span.*?">(.*?)</span',con,re.S|re.M).group(1)
                        building.bu_floor = re.search('层数.*?<span.*?">(.*?)</span',con,re.S|re.M).group(1)
                        building.bu_all_house = re.search('预售套数.*?<span.*?">(.*?)</span',con,re.S|re.M).group(1)
                        building.bu_pre_sale_date = re.search('有效期.*?<span.*?">(.*?)</span',con,re.S|re.M).group(1)
                        building.bu_type = re.search('土地用途.*?<span.*?">(.*?)</span',con,re.S|re.M).group(1)
                        building.bu_pre_sale = re.search('许可证编号.*?<span.*?">(.*?)</span',con,re.S|re.M).group(1)
                        building.insert_db()

                        house_list = re.findall('房号:<a href="(.*?)"', con)
                        for ho in house_list:
                            try:
                                house = House(co_index)
                                house_url = 'http://www.jyfg.cn/HouseWebSetup/PublicReport/' + ho
                                respon = requests.get(house_url)
                                html = respon.text
                                house.co_id = comm.co_id
                                house.bu_id = building.bu_id
                                house.ho_name = re.search('房号:.*?<span.*?>(.*?)<', html, re.M | re.S).group(1)
                                house.ho_build_size = re.search('预测建筑面积:.*?<span.*?>(.*?)<', html, re.M | re.S).group(1)
                                house.ho_true_size = re.search('预测套内面积:.*?<span.*?>(.*?)<', html, re.M | re.S).group(1)
                                house.ho_share_size = re.search('预测分摊面积:.*?<span.*?>(.*?)<', html, re.M | re.S).group(1)
                                house.ho_type = re.search('房屋用途:.*?<span.*?>(.*?)<', html, re.M | re.S).group(1)
                                house.ho_room_type = re.search('户型结构:.*?<span.*?>(.*?)<', html, re.M | re.S).group(1)

                                house.insert_db()
                            except Exception as e:
                                print("co_index={},房屋{}信息提取失败".format(co_index,house_url))
                                print(e)
                                continue
                    except Exception as e:
                        print(e)
                        print('co_idnex={},楼栋{}提取失败'.format(co_index,build_url))
                        continue
            except Exception as e:
                print('co_index={},小区{}提取失败'.format(co_index,comm_url))
                print(e)
                continue


if __name__ == '__main__':
    j = Jieyang()
    j.start_crawler()
