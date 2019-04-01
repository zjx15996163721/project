from gevent import monkey
monkey.patch_all()
import requests
import pika
import json
from lib.proxy_iterator import Proxies
from lxml import etree
from lib.log import LogHandler
import re
from office_building_info import OfficeBuilding
from retry import retry
import gevent
import threading
p = Proxies()
log = LogHandler('all_anjuke_consumer')

class VerifyError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo


#写字楼楼盘的消费者
class AnjukeLoupanConsumer:
    def __init__(self,proxies):
        self.proxies = proxies
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='114.80.150.196',
            port=5673,
            heartbeat=0
        ))
        self.detail_channel = self.connection.channel()
        self.detail_channel.queue_declare(queue='loupan_office_detail_url', durable=True)
        self.loupanconsumer_list = []

    def start_consume(self):
        self.detail_channel.basic_qos(prefetch_count=1)
        self.detail_channel.basic_consume(
            self.callback,
            queue='loupan_office_detail_url'
        )
        self.detail_channel.start_consuming()

    def callback(self,ch,method,properties,body):
        detail_dict = json.loads(body.decode())
        for key, value in detail_dict.items():
            base_url = key
            detail_urls = value
            for base_detail_url in detail_urls:
                result = re.search('/loupan/(\d+)', base_detail_url)
                if result:
                    loupan_id = result.group(1)
                    print(loupan_id)
                else:
                    log.error('没有匹配到楼盘id{}'.format(base_detail_url))
                    continue
                detail_url = base_url + '/loupan/canshu/' + str(loupan_id)
                if len(self.loupanconsumer_list) == 100:
                     # todo 100线程
                     for url in self.loupanconsumer_list:
                         threading.Thread(target=self.send_detail_url, args=(url,)).start()
                     self.loupanconsumer_list.clear()
                else:
                    self.loupanconsumer_list.append(detail_url)
        ch.basic_ack(delivery_tag=method.delivery_tag)


            # jobs = [gevent.spawn(self.send_detail_url, base_detail_url,base_url) for base_detail_url in detail_urls]
            # gevent.wait(jobs)

            # for base_detail_url in detail_urls:
            #     self.send_detail_url(base_detail_url,base_url)
        # ch.basic_ack(delivery_tag=method.delivery_tag)



    @retry(logger=log,delay=2)
    def send_detail_url(self,detail_url):
        # result = re.search('/loupan/(\d+)',base_detail_url)
        # if result:
        #     loupan_id = result.group(1)
        #     print(loupan_id)
        # else:
        #     log.error('没有匹配到楼盘id{}'.format(base_detail_url))
        #     return
        # #楼盘详细参数：https://sh.xzl.anjuke.com/loupan/canshu/10099
        # detail_url = base_url+ '/loupan/canshu/' + str(loupan_id)
        # print(detail_url)
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res = requests.get(detail_url,headers=self.headers,proxies=self.proxies)
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in res.text:
            raise VerifyError('返回结果不是想要的结果')
        if '访问验证-安居客' in res.text:
            raise VerifyError('出现滑块验证码')
        office = OfficeBuilding(source='anjuke')
        office.url = detail_url
        detail_res = etree.HTML(res.text)
        #楼盘参数：https://sh.xzl.anjuke.com/loupan/canshu/10099
        #获取城市
        city_list = detail_res.xpath('//div[@class="cityselect"]/div[@class="city-view"]/text()')
        if len(city_list)>0:
            # city_string = city_list[0]
            city = ''.join(city_list)
            office.city = ''.join(city.split())

        #楼盘概况
        loupan_info_list = detail_res.xpath('//div[@id="content"]/div[@class="mod"][1]/ul[@class="param-detail-mod clearfix"]/li')
        for info in loupan_info_list:
            info_tag_list = info.xpath('label/text()')
            info_tag_value_list = info.xpath('span/text()')
            if len(info_tag_list)>0 and len(info_tag_value_list)>0:
                info_tag = info_tag_list[0]
                info_tag_value = info_tag_value_list[0]
                if '楼盘' in info_tag:
                    office.name = info_tag_value
                elif '地址' in info_tag:
                    office.address = info_tag_value
                    office.region = info_tag_value
                elif '类型' in info_tag:
                    office.office_type = info_tag_value
                elif '级别' in info_tag:
                    office.bed_kind = info_tag_value
        #楼盘配套
        loupan_mating_list = detail_res.xpath('//div[@id="content"]/div[@class="mod"][2]/ul[@class="param-detail-mod clearfix"]/li')
        for mating in loupan_mating_list:
            mating_tag_list = mating.xpath('label/text()')
            mating_tag_value_list = mating.xpath('span/text()')
            if len(mating_tag_list)>0 and len(mating_tag_value_list)>0:
                mating_tag = mating_tag_list[0]
                mating_tag_value = mating_tag_value_list[0]
                if '物业费' in mating_tag:
                    office.estate_charge = mating_tag_value
                elif '空调类型' in mating_tag:
                    office.conditioner = mating_tag_value
                elif '客梯' in mating_tag:
                    person_elevators_count_string = mating_tag_value
                    ele_per__result = re.search('(\d+)部',person_elevators_count_string)
                    if ele_per__result:
                        office.person_elevators_count = int(ele_per__result.group(1))
                    else:
                        office.person_elevators_count = 0
                elif '货梯' in mating_tag:
                    goods_elevator_count_string = mating_tag_value
                    ele_goo_result = re.search('(\d+)部', goods_elevator_count_string)
                    if ele_goo_result:
                        office.goods_elevator_count = int(ele_goo_result.group(1))
                    else:
                        office.goods_elevator_count = 0
                elif '电梯品牌' in mating_tag:
                    office.elevator_brand = mating_tag_value
                elif '车位月租金' in mating_tag:
                    office.parking_fee = mating_tag_value
                elif '地上车位数' in mating_tag:
                    land_car_site_string = mating_tag_value
                    land_car_result = re.search('(\d+)个', land_car_site_string)
                    if land_car_result:
                        office.land_car_site = int(land_car_result.group(1))
                    else:
                        office.land_car_site = 0
                elif '网络通讯' in mating_tag:
                    office.network_way = mating_tag_value
                elif '地下车位数' in mating_tag:
                    underground_car_site_string = mating_tag_value
                    underground_car_result = re.search('(\d+)个', underground_car_site_string)
                    if underground_car_result:
                        office.underground_car_site = int(underground_car_result.group(1))
                    else:
                        office.underground_car_site = 0
                elif '物业公司' in mating_tag:
                    office.estate_company = mating_tag_value
                elif '楼内配套' in mating_tag:
                    office.build_facilities = mating_tag_value
                elif '空调开放时间' in mating_tag:
                    office.conditioner_time = mating_tag_value
                elif '安防系统' in mating_tag:
                    office.safe_system = mating_tag_value
            if office.underground_car_site is not None and office.land_car_site is not None:
                office.car_site_count = office.underground_car_site + office.land_car_site
            if office.person_elevators_count is not None and office.goods_elevator_count is not None:
                office.elevators_count = office.person_elevators_count + office.goods_elevator_count

        #楼盘参数
        loupan_params_list = detail_res.xpath('//div[@id="content"]/div[@class="mod"][3]/ul[@class="param-detail-mod clearfix"]/li')
        for param in loupan_params_list:
            param_tag_list = param.xpath('label/text()')
            param_tag_value_list = param.xpath('span/text()')
            if len(param_tag_list)>0 and len(param_tag_value_list)>0:
                param_tag = param_tag_list[0]
                param_tag_value = param_tag_value_list[0]
                if '总楼层' in param_tag:
                    office.total_floor = param_tag_value
                elif '竣工时间' in param_tag:
                    office.finish_building_date = param_tag_value
                elif '总建筑面积' in param_tag:
                    office.build_area = param_tag_value
                elif '标准层面积' in param_tag:
                    office.standard_area = param_tag_value
                elif '标准层高' in param_tag:
                    office.standard_height = param_tag_value
                elif '净高' in param_tag:
                    office.clear_height = param_tag_value
                elif '是否涉外' in param_tag:
                    office.is_foreign = param_tag_value
                elif '大堂层高' in param_tag:
                    office.lobby_height = param_tag_value
                elif '是否可注册' in param_tag:
                    office.is_register = param_tag_value
                elif '开间面积' in param_tag:
                    office.bay_area = param_tag_value
                elif '开发商' in param_tag:
                    office.developer = param_tag_value

        office.insert_db()






#写字楼新盘的消费者
class AnjukeNewConsumer:
    def __init__(self,proxies):
        self.proxies = proxies
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='114.80.150.196',
            port=5673,
            heartbeat=0
        ))
        self.detail_channel = self.connection.channel()
        self.detail_channel.queue_declare(queue='new_office_detail_url', durable=True)
        self.newconsumer_list = []

    def start_consume(self):
        self.detail_channel.basic_qos(prefetch_count=1)
        self.detail_channel.basic_consume(
            self.callback,
            queue='new_office_detail_url'
        )
        self.detail_channel.start_consuming()

    def callback(self,ch,method,properties,body):
        detail_urls = json.loads(body.decode())
        for detail_url in detail_urls:
            if len(self.newconsumer_list) == 100:
                # todo 100线程

                for url in self.newconsumer_list:
                    threading.Thread(target=self.send_detail_url, args=(url,)).start()
                self.newconsumer_list.clear()
            else:
                self.newconsumer_list.append(detail_url)
        ch.basic_ack(delivery_tag=method.delivery_tag)

        # jobs = [gevent.spawn(self.send_detail_url, detail_url) for detail_url in detail_urls]
        # gevent.wait(jobs)
        # ch.basic_ack(delivery_tag=method.delivery_tag)

    #楼盘详情url:https://sh.fang.anjuke.com/loupan/canshu-250374.html?from=loupan_tab
    #楼盘主页url:https://sh.fang.anjuke.com/loupan/250374.html?from=AF_RANK_1
    @retry(logger=log, delay=2)
    def send_detail_url(self,detail_url):
        print(detail_url)
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        res = requests.get(detail_url, headers=self.headers, proxies=self.proxies)
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in res.text:
            raise VerifyError('返回结果不是想要的结果')
        if '访问验证-安居客' in res.text:
            raise VerifyError('出现滑块验证码')
        office = OfficeBuilding(source='anjuke')
        office.url  = detail_url
        detail_res = etree.HTML(res.text)
        #产权年限
        li_list = detail_res.xpath('//div[@class="clearfix"]/ul[@class="info-left"]/li')
        for li in li_list:
            li_tag_list = li.xpath('label/text()')
            li_tag_value_list = li.xpath('span/text()')
            if len(li_tag_list)>0 and len(li_tag_value_list)>0:
                li_tag = li_tag_list[0]
                li_tag_value = li_tag_value_list[0]
                if '产权年限' in li_tag:
                    office.property_life = li_tag_value

        #获取楼盘详情页的url,,第二次发送请求
        detail_a_list = detail_res.xpath('//div[@class="lp-nav"]/ul[@class="lp-navtabs clearfix"]/li[2]/a')
        if len(detail_a_list)>0:
            detail_a = detail_a_list[0]
            text = detail_a.xpath('text()')[0]
            if '楼盘详情' in text:
                url = detail_a.xpath('@href')[0]
            else:
                return
            detail_result = self.new_detail_send(url)
            detail_html = etree.HTML(detail_result.content.decode())
            #城市
            city_list = detail_html.xpath('//div[@class="site-search clearfix"]/div[@class="crumb-item fl"]/a[1]/text()')
            if len(city_list) > 0:
                city_string = city_list[0]
                print(city_string)
                city = re.search('(.*?)安居客', city_string)
                print(city.group(1))
                if city:
                    office.city = city.group(1)
                else:
                    return
            detail_li_list = detail_html.xpath('//div[@class="can-left"]/div/div[@class="can-border"]/ul/li')
            for detail_li in detail_li_list:
                detail_tag_list = detail_li.xpath('div[@class="name"]/text()')
                detail_tag_value_list = detail_li.xpath('div[@class="des"]//text()')
                if len(detail_tag_list)>0 and len(detail_tag_value_list)>0:
                    detail_tag = detail_tag_list[0]
                    # detail_tag_value = ''.join(detail_tag_value_list)
                    detail_tag_value = detail_tag_value_list
                    if '楼盘名称' in detail_tag:
                        name_string = detail_tag_value[0]
                        name = ''.join(name_string)
                        office.name = ','.join(name.split())
                    elif '楼盘特点' in detail_tag:
                        characteristic_string =  detail_tag_value
                        characteristic = ''.join(characteristic_string)
                        office.characteristic = ','.join(characteristic.split())
                    elif '写字楼类型' in detail_tag:
                        office_type_string = detail_tag_value
                        office_type = ''.join(office_type_string)
                        office.office_type = ''.join(office_type.split())
                    elif '写字楼级别' in detail_tag:
                        office.bed_kind = detail_tag_value[0]
                    elif '开发商' in detail_tag:
                        developer_string = detail_tag_value
                        developer = ''.join(developer_string)
                        office.developer = ''.join(developer.split())
                    elif '区域' in detail_tag:
                        region_string = detail_tag_value
                        region = ''.join(region_string)
                        office.region = ''.join(region.split())
                    elif '楼盘地址' in detail_tag:
                        address_string = detail_tag_value[0]
                        address = ''.join(address_string)
                        office.address = ''.join(address.split())
                    elif '开间面积' in detail_tag:
                        bay_area_string = detail_tag_value
                        bay_area = ''.join(bay_area_string)
                        office.bay_area = ''.join(bay_area.split())
                    elif '最新开盘' in detail_tag:
                        open_date_string = detail_tag_value
                        open_date = ''.join(open_date_string)
                        office.open_date = ''.join(open_date.split())
                    elif '交房时间' in detail_tag:
                        finish_date_string = detail_tag_value[0]
                        finish_building_date = ''.join(finish_date_string)
                        office.finish_building_date = ''.join(finish_building_date.split())
                    elif '出售类型' in detail_tag:
                        sell_type_string = detail_tag_value
                        sell_type = ''.join(sell_type_string)
                        office.sell_type = ''.join(sell_type.split())
                    elif '出租类型' in detail_tag:
                        rent_type_string = detail_tag_value
                        rent_type = ''.join(rent_type_string)
                        office.rent_type = ''.join(rent_type.split())
                    elif '装修' in detail_tag:
                        office.fitment = detail_tag_value[0]
                    elif '得房率' in detail_tag:
                        real_use_percent_string = detail_tag_value
                        real_use_percent = ''.join(real_use_percent_string)
                        office.real_use_percent = ''.join(real_use_percent.split())
                    elif '标准层面积' in detail_tag:
                        standard_area_string = detail_tag_value
                        standard_area = ''.join(standard_area_string)
                        office.standard_area = ''.join(standard_area.split())
                    elif '物业管理费' in detail_tag:
                        office.estate_charge = detail_tag_value[0]
                    elif '物业公司' in detail_tag:
                        estate_company_string = detail_tag_value
                        estate_company = ''.join(estate_company_string)
                        office.estate_company = ''.join(estate_company.split())
                    elif '是否分割' in detail_tag:
                        divisible_string = detail_tag_value
                        divisible = ''.join(divisible_string)
                        office.divisible = ''.join(divisible.split())
                    elif '绿化率' in detail_tag:
                        virescence_percent_string = detail_tag_value
                        virescence_percent = ''.join(virescence_percent_string)
                        office.virescence_percent = ''.join(virescence_percent.split())
                    elif '楼层状况' in detail_tag:
                        floor_info_string = detail_tag_value
                        floor_info = ''.join(floor_info_string)
                        office.floor_info = ''.join(floor_info.split())
                    elif '工程进度' in detail_tag:
                        floor_info_string = detail_tag_value[0]
                        if '竣工时间' in floor_info_string:
                            finish_time = re.search('竣工时间：(.*)',floor_info_string)
                            if finish_time:
                                office.finish_building_date = finish_time.group(1)
                    elif '车位数' in detail_tag:
                        car_site_count_string = detail_tag_value[0]
                        result = re.search('(\d+)', car_site_count_string)
                        result1 = re.search('地上：(\d+)个', car_site_count_string)
                        result2 = re.search('地下：(\d+)个', car_site_count_string)
                        if result:
                            office.car_site_count = int(result.group(1))
                        else:
                            office.car_site_count = detail_tag_value
                        if result1:
                            office.land_car_site = int(result1.group(1))
                        else:
                            office.land_car_site = 0
                        if result2:
                            office.underground_car_site = int(result2.group(1))
                        else:
                            office.underground_car_site = 0
            #预售许可证
            licence_list = detail_html.xpath('//div[@class="can-left"]/div/div[@class="can-border"]/ul/li/div[@class="des licence"]//text()')
            if len(licence_list)>0:
                licence = licence_list[0]
                result = re.findall('(.*?)；', licence)
                office.licence = ','.join(result)
        office.insert_db()

    @retry(logger=log,delay=2)
    def new_detail_send(self,url):
        requests.get('http://ip.dobel.cn/switch-ip', proxies=self.proxies)
        detail_result = requests.get(url, headers=self.headers, proxies=self.proxies)
        if '系统检测到您正在使用网页抓取工具访问安居客网站' in detail_result.text:
            raise VerifyError('返回结果不是想要的结果')
        if '访问验证-安居客' in detail_result.text:
            raise VerifyError('出现滑块验证码')
        else:
            return detail_result



# if __name__ == '__main__':
    # a = AnjukeZuConsumer(proxies=next(p))
    # a.start_consume()




















