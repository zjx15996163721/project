"""
url = http://old.newhouse.cnnbfdc.com/lpxx.aspx
city : 奉化
CO_INDEX : 73
小区数量：
对应关系：
    小区与楼栋：
    楼栋与房屋：
author: 程纪文
"""
import requests
from backup.comm_info import Comm, Building, House
import re
from backup.crawler_base import Crawler
from lxml import etree
import time

url = 'http://old.newhouse.cnnbfdc.com/lpxx.aspx'
co_index = '73'
city = '奉化'


class Fenghua(Crawler):
    def __init__(self):
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119Safari/537.36',
        }

    def start_crawler(self):
        res = requests.get(url, headers=self.headers)
        html = res.text
        page = re.search('>><.*?p=(.*?)"', html, re.S | re.M).group(1)
        for i in range(1, int(page) + 1):
            page_url = 'http://old.newhouse.cnnbfdc.com/lpxx.aspx?p=' + str(i)
            response = requests.get(page_url, headers=self.headers)
            content = response.text
            comm_url_list = re.findall('align="left" bgcolor="#FFFFFF".*?href="(.*?)"', content, re.S | re.M)
            self.get_comm_info(comm_url_list)

    def get_comm_info(self, comm_url_list):
        for i in comm_url_list:
            comm = Comm(co_index)
            comm_url = 'http://old.newhouse.cnnbfdc.com/' + i
            try:
                response = requests.get(comm_url, headers=self.headers)
            except Exception as e:
                print("{}城市无法访问小区{}".format(city,comm_url),e)
                continue

            html = response.text
            con = etree.HTML(html)
            comm.co_id = re.search('id=(\d+)',i).group(1)
            comm.co_name = re.findall('项目名称：.*?<span.*?>(.*?)<', html, re.S | re.M)[0]
            comm.co_address = re.findall('项目地址：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
            comm.co_develops = re.findall('开发公司：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
            comm.co_pre_sale = re.findall('售证名称：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
            comm.co_build_size = re.findall('纳入网上可售面积：.*?<img.*?>(.*?)<', html, re.S | re.M)[0]
            comm.co_all_house = re.findall('纳入网上可售套数：.*?<img.*?>(.*?)<', html, re.S | re.M)[0]
            comm.area = re.findall('所在区县：.*?<td.*?>(.*?)<', html, re.S | re.M)[0]
            comm.insert_db()
            bu_all_house_list = re.findall('window.open.*?center.*?center.*?>(.*?)<', html, re.S | re.M)
            try:
                bu_url_list = re.findall("window\.open\('(.*?)'", html, re.S | re.M)
            except Exception as e:
                print("{}城市{}小区无楼栋".format(city,comm.co_name),e)
                continue
            for i in range(len(bu_url_list)):
                build = Building(co_index)
                bu_url = bu_url_list[i]
                build.bu_all_house = bu_all_house_list[i]
                build.co_name = comm.co_name
                build.bu_num = con.xpath("//a[@href='#']/@title")[i]
                build.bu_id = re.search('key=(\d+)&',bu_url).group(1)
                build.co_id = comm.co_id
                build.insert_db()
                self.get_house_info(bu_url,build.bu_id)

    def get_house_info(self, bu_url,bu_id):
        qrykey = re.search('qrykey=(.*?)&', bu_url).group(1)
        house_url = 'http://old.newhouse.cnnbfdc.com/GetHouseTable.aspx?qrykey=' + qrykey
        response = requests.get(house_url, headers=self.headers)
        html = response.text
        house_code_list = re.findall("onclick=select_room\('(.*?)'", html, re.S | re.M)
        for i in house_code_list:
            house_detail_url = 'http://old.newhouse.cnnbfdc.com/openRoomData.aspx?roomId='+str(i)
            # while True:
            #     proxies = self.proxy_pool()
            try:
                res = requests.get(house_detail_url,headers=self.headers,)
            except Exception as e:
                print("{}城市无法访问房屋页面{}".format(city,house_detail_url),e)
                continue
                # if res.status_code ==200:
            time.sleep(2)
                #     self.proxy_status(proxies,0)
                #     break
                # else:
                #     self.proxy_status(proxies,1)
                #     continue
            content = res.text
            ho = House(co_index)
            ho.bu_id = bu_id
            try:
                ho.ho_name = re.search('室号.*?">(.*?)</td>',content,re.S|re.M).group(1)
                ho.ho_floor = re.search('楼层.*?">(.*?)</td>',content,re.S|re.M).group(1)
                ho.ho_room_type = re.search('户型.*?">(.*?)</td>',content,re.S|re.M).group(1)
                ho.ho_type = re.search('用途.*?">(.*?)</td>',content,re.S|re.M).group(1)
                ho.ho_build_size = re.search('预测建筑面积.*?">(.*?)</td>',content,re.S|re.M).group(1)
                ho.ho_true_size = re.search('预测套内面积.*?">(.*?)</td>',content,re.S|re.M).group(1)
                ho.ho_share_size =re.search('预测分摊面积.*?">(.*?)</td>',content,re.S|re.M).group(1)

                ho.insert_db()
            except Exception as e:
                print("{}房号错误，请求频繁,当前页面{}未提取".format(city,house_detail_url),e)
                continue

# def proxy_pool(self):
#     api_1 = "http://192.168.0.235:8999/get_one_proxy"
#     data = {"app_name":"fenghua"}
#     proxy_ip = requests.post(api_1,data=data)
#     ip = "http://"+proxy_ip.text
#     proxy_ip = {"http":ip}
#     print(proxy_ip)
#     return proxy_ip

# def proxy_status(self,proxies,code):
#     api_2 = "http://192.168.0.235:8999/send_proxy_status"
#     ip = proxies["http"]
#     ip = re.search('//(.*?)',ip).group(1)
#     data = {"app_name":"fenghua",
#             "status_code":code,
#             "ip":ip}
#     requests.post(api_2,data=data)
