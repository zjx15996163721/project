"""
百度迁徙
selenium+chrome
这个不用了
"""

from selenium import webdriver
import time
import datetime
from lib.mongo import Mongo
from baiduqianxi.city_list import CITY_LIST


class Baiduqianxi:
    @staticmethod
    def get_baiduqianxi():
        m = Mongo('192.168.0.235', 27017, 'baiduqianxi', 'baiduqianxi')
        coll = m.get_collection_object()

        browser = webdriver.ChromeOptions()
        browser.add_argument('--headless')
        browser = webdriver.Chrome(chrome_options=browser, executable_path='chromedriver.exe')
        browser.set_window_size(1600, 900)

        for city in CITY_LIST:
            browser.get('http://qianxi.baidu.com/')
            try:
                time.sleep(3)
                elem = browser.find_element_by_id('input_cityName')
                elem.send_keys(city)
                time.sleep(1)
                browser.find_element_by_class_name('input-group-addon').click()
                time.sleep(5)
                in_data = browser.find_element_by_class_name('div_list_container')
                in_info = in_data.text
                print(in_info)
                in_list = in_info.split('\n')
                in_dict = {}
                for i in in_list:
                    list_ = i.split(' ')
                    city_name = list_[1].replace(city, '')
                    number = list_[2].replace('％', '')
                    in_dict[city_name] = number

                browser.find_element_by_xpath('//a[@class="btn btn-default"]').click()
                out_data = browser.find_element_by_class_name('div_list_container')
                out_info = out_data.text
                print(out_info)
                out_list = out_info.split('\n')
                out_dict = {}
                for i in out_list:
                    list_ = i.split(' ')
                    city_name = list_[1].replace(city, '')
                    number = list_[2].replace('％', '')
                    out_dict[city_name] = number
                coll.insert_one({
                    'city': city,
                    'in': in_dict,
                    'out': out_dict,
                    'insert_time': datetime.datetime.now(),
                    'date': int(str(datetime.date.today()).replace('-', ''))
                })
            except Exception as e:
                print(e)
                print(city)
        browser.close()
