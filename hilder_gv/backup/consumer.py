import json
from lxml import etree
import re
from backup.comm_info import Comm, Building, House
import yaml

setting = yaml.load(open('config_local.yaml'))
from lib.rabbitmq import Rabbit


class Consumer(object):
    r = Rabbit(host=setting['rabbitmq_host'], port=setting['rabbitmq_port'])
    channel = r.get_channel()
    channel.queue_declare(queue='hilder_gv')

    def callback(self, ch, method, properties, body):
        body = json.loads(body.decode())
        analyzer_rules_dict = body['analyzer_rules_dict']
        analyzer_type = body['analyzer_type']
        co_index = analyzer_rules_dict['co_index']
        data_type = analyzer_rules_dict['data_type']
        html = body['html']
        try:
            self.common_use(analyzer_type, co_index, data_type, html, analyzer_rules_dict)
        except Exception as e:
            print(e)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def common_use(self, analyzer_type, co_index, data_type, html, analyzer_rules_dict):
        if data_type == 'comm':
            info = self.rule_data(analyzer_type, analyzer_rules_dict, html)
            try:
                self.put_database(info, data_type, co_index=co_index)
            except Exception as e:
                print(e)
        elif data_type == 'build':
            co_id_rule = analyzer_rules_dict['co_id']
            co_name_rule = analyzer_rules_dict['co_name']
            co_id = self.rule_type(analyzer_type, html, co_id_rule)
            co_name = self.rule_type(analyzer_type, html, co_name_rule)
            co_id = self.have_no_have(co_id)
            co_name = self.have_no_have(co_name)
            del analyzer_rules_dict['co_id']
            del analyzer_rules_dict['co_name']
            info = self.rule_data(analyzer_type, analyzer_rules_dict, html)
            try:
                self.put_database(info, data_type, co_index=co_index, co_id=co_id, co_name=co_name)
            except Exception as e:
                print(e)
        elif data_type == 'house':
            bu_id_rule = analyzer_rules_dict['bu_id']
            bu_num_rule = analyzer_rules_dict['bu_num']

            bu_id = self.rule_type(analyzer_type, html, bu_id_rule)
            bu_num = self.rule_type(analyzer_type, html, bu_num_rule)
            bu_id = self.have_no_have(bu_id)
            bu_num = self.have_no_have(bu_num)
            del analyzer_rules_dict['bu_id']
            del analyzer_rules_dict['bu_num']
            info = self.rule_data(analyzer_type, analyzer_rules_dict, html)
            try:
                self.put_database(info, data_type, co_index=co_index, bu_id=bu_id, bu_num=bu_num)
            except Exception as e:
                print(e)

    def rule_type(self, rule_type, html, rule):
        if rule:
            if rule_type == 'regex':
                data = re.findall(rule, html, re.S | re.M)
                return data
            else:
                tree = etree.HTML(html)
                data = tree.xpath(rule)
                return data
        else:
            return None

    @staticmethod
    def rule_data(analyzer_type, analyzer_rules_dict, html):
        tree = etree.HTML(html)
        info = {}
        for i in analyzer_rules_dict:
            if not analyzer_rules_dict[i]: continue
            if i == 'co_index' or i == 'data_type': continue
            if analyzer_type == 'regex':
                info_list = re.findall(analyzer_rules_dict[i], html, re.M | re.S)
            else:
                info_list = tree.xpath(analyzer_rules_dict[i])
            if info_list:
                info[i] = info_list
            if not info: print('\n\n没有选取到任何信息\n\n')
        return info

    @staticmethod
    def have_no_have(num):
        if num:
            return num[0]
        else:
            return None

    @staticmethod
    def add_attr(obj, info, index):
        for key, value in info.items():
            if value:
                setattr(obj, key, value[index].strip())
        obj.insert_db()

    # 遍历字典放入数据库
    def put_database(self, info, analyzer, co_index, bu_id=None, bu_num=None, co_id=None, co_name=None):
        key = sorted(info.items())[0][0]
        length = len(info[key])
        for i in range(0, length):
            obj = self.get_data_obj(analyzer, co_index)
            if analyzer == 'comm':
                pass
            elif analyzer == 'build':
                if co_id: setattr(obj, 'co_id', co_id)
                if co_name: setattr(obj, 'co_name', co_name)
            elif analyzer == 'house':
                if bu_id:
                    setattr(obj, 'bu_id', bu_id.strip())
                if bu_num:
                    setattr(obj, 'bu_num', bu_num.strip())
            self.add_attr(obj, info, i)

    # 创建对象（data_type是什么类型是就创建什么对象）
    def get_data_obj(self, analyzer, co_index):
        if analyzer == 'comm':
            return Comm(co_index)
        elif analyzer == 'build':
            return Building(co_index)
        elif analyzer == 'house':
            return House(co_index)

    def consume_queue(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue='hilder_gv')
        self.channel.start_consuming()


if __name__ == '__main__':
    consumer = Consumer()
    consumer.consume_queue()
