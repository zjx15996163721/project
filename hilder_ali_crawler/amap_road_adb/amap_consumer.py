# -*- coding: utf-8 -*-
import pika
import json
import time
import os
import time
import subprocess
import re
from multiprocessing import Process

# from amap_road_adb.android_control import AutoAdb

rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='192.168.10.10',
    port=5673,
    heartbeat=0
))

rabbit_channel = rabbit_connection.channel()
rabbit_channel.queue_declare(queue='amap_adb_street')


class AutoAdb:
    def __init__(self, device_number=None):
        self.device_number = device_number
        adb_path = os.path.join('adb')
        print(adb_path)
        try:
            subprocess.Popen(
                [adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.adb_path = adb_path
        except OSError:
            pass
        else:
            try:
                subprocess.Popen(
                    [adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except OSError:
                pass

    def get_screen(self):
        process = os.popen(self.adb_path + ' shell wm size')
        output = process.read()
        return output

    def run(self, raw_command):
        # print(raw_command)
        command = '{} {}'.format(self.adb_path, raw_command)
        print(command)
        process = os.popen(command)
        output = process.read()
        return output

    def test_device(self):
        print('检查设备是否连接...')
        command_list = [self.adb_path, 'devices']
        process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.communicate()
        if output[0].decode('utf8') == 'List of devices attached\n\n':
            print('未找到设备')
            print('adb 输出:')
            for each in output:
                print(each.decode('utf8'))
            exit(1)
        print('设备已连接')
        print('adb 输出:')
        for each in output:
            print(each.decode('utf8'))

    def test_density(self):
        process = os.popen(self.adb_path + ' shell wm density')
        output = process.read()
        return output

    def test_device_detail(self):
        process = os.popen(self.adb_path + ' shell getprop ro.product.device')
        output = process.read()
        return output

    def test_device_os(self):
        process = os.popen(self.adb_path + ' shell getprop ro.build.version.release')
        output = process.read()
        return output

    def adb_path(self):
        return self.adb_path

    def start_app(self, amap_package_name):
        self.run('-s {} shell am start -n {}'.format(self.device_number, amap_package_name))

    def stop_app(self, amap_package_name):
        self.run('-s {} shell am force-stop {}'.format(self.device_number, amap_package_name))


class AmapAdbConsume:
    def __init__(self, cmd, device_number):
        self.cmd = cmd
        self.device_number = device_number

    def start_consume(self):
        rabbit_channel.basic_qos(prefetch_count=1)
        rabbit_channel.basic_consume(self.callback, queue='amap_adb_street')
        rabbit_channel.start_consuming()

    def callback(self, ch, method, properties, body):
        param = json.loads(body.decode())
        self.adb_control(self.cmd, self.device_number, param)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def adb_control(self, c, device_number, param):
        c.run('-s {} shell input tap 117 73'.format(device_number))  # 点击定位到输入框
        time.sleep(2)
        c.run('-s {} shell am broadcast -a ADB_INPUT_TEXT --es msg {}'.format(device_number, param))  # 输入文本内容
        c.run('-s {} shell input tap 679 69'.format(device_number))  # 点击搜索
        time.sleep(2)  # 等待0.5秒
        c.run('-s {} shell input tap 33 94'.format(device_number))  # 清空搜索列表
        print('{}设备输出的'.format(device_number))


if __name__ == '__main__':
    cmd = AutoAdb()
    amap_package_class_name = 'com.autonavi.minimap/com.autonavi.map.activity.NewMapActivity'
    # 连接到设备
    # cmd.run('connect 127.0.0.1:62001')
    device_str = cmd.run('devices')
    device_number_list = []
    for i in re.findall('(127.*?)	device', device_str, re.S | re.M):
        device_number_list.append(i)
    for device_number in device_number_list:
        cmd.start_app(amap_package_class_name)
        Process(target=AmapAdbConsume(cmd, device_number).start_consume).start()
