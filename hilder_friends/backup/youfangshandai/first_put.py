import requests
import json
import pika
import certifi


class Construction(object):
    def __init__(self):
        # 建立实例，声明管道，声明队列
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.190', port=5673))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='yfsd_construction')
        self.city_dict = {
            '北京': 'https://bjset.cmbc.com.cn',
            '武汉': 'https://yfsdwh.cmbc.com.cn',
            '石家庄': 'https://yfsdsjz.cmbc.com.cn',
            '郑州': 'https://yfsdzz.cmbc.com.cn',
            '南昌': 'https://yfsdnac.cmbc.com.cn',
            '福州': 'https://yfsdfuz.cmbc.com.cn',
            '兰州': 'https://yfsdlaz.cmbc.com.cn',
            '呼和浩特': 'https://yfsdhuh.cmbc.com.cn',
            '宁波': 'https://yfsdnib.cmbc.com.cn',
            '贵阳': 'https://yfsdguy.cmbc.com.cn',
            '哈尔滨': 'https://yfsdhrb.cmbc.com.cn',
            '昆明': 'https://yfsdkum.cmbc.com.cn',
            '太原': 'https://yfsdtay.cmbc.com.cn',
            '苏州': 'https://yfsdsuz.cmbc.com.cn',
            '杭州': 'https://yfsdhaz.cmbc.com.cn',
            '温州': 'https://yfsdwez.cmbc.com.cn',
        }

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
        }

        # 直接用本机请求
        self.count = 0

    def get_constructionId(self):
        for city in self.city_dict:
            try:
                # pagesize 100000
                data = {'keyworks': '', 'pageNo': '1', 'pageSize': '100000'}
                city_url = self.city_dict[city]
                url = city_url + '/wxp/yfsd/queryBuildingByPage'
                response = requests.post(url=url, data=data, headers=self.headers, verify=False)
                constructionId_info = json.loads(response.text)
                for con in constructionId_info['resultData']:
                    """
                    con
                       {
                        "constructionId": 9385,
                        "constructionName": "毛纺北小区",
                        "pinyin": null,
                        "saleName": null,
                        "address": null,
                        "loopLine": null,
                        "endDate": null,
                        "areaName": null,
                        "conArrea": null,
                        "cityId": null,
                        "dataChannel": "WU"
                    },
                    """

                    con_id = (con['constructionId'])
                    # 编辑要放入队列里的数据
                    data = {
                        'city_url': city_url,
                        'con_id': con_id,
                        'city': city,
                    }
                    print(data)
                    # 放入队列
                    self.channel.basic_publish(exchange='',
                                               routing_key='yfsd_construction',
                                               body=json.dumps(data))
                    self.count = self.count + 1
                    print('放入队列%s次' % self.count)

            except Exception as e:
                print(e)
                continue
        self.connection.close()


if __name__ == '__main__':
    con = Construction()
    con.get_constructionId()
