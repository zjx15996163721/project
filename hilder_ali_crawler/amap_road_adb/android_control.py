# -*- coding: utf-8 -*-
import os
import subprocess
import re
from multiprocessing import Process


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


def start_device(cmd, device_number):
    amap_package_class_name = 'com.autonavi.minimap/com.autonavi.map.activity.NewMapActivity'
    amap_package_name = 'com.autonavi.minimap'
    cmd.device_number = device_number
    cmd.start_app(amap_package_class_name)

    # cmd.run('-s {} shell am start -n {}'.format(device_number, amap_package_name))
    # cmd.run('-s {} shell am force-stop {}'.format(device_number, 'com.autonavi.minimap'))
    # while True:
    #     c.run('-s {} shell input tap 117 73'.format(device_number))  # 点击定位到输入框
    #     time.sleep(2)
    #     c.run('-s {} shell am broadcast -a ADB_INPUT_TEXT --es msg "金钟路100号"'.format(device_number))  # 输入文本内容
    #     c.run('-s {} shell input tap 679 69'.format(device_number))  # 点击搜索
    #     time.sleep(2)  # 等待0.5秒
    #     c.run('-s {} shell input tap 33 94'.format(device_number))  # 清空搜索列表
    #     print('{}设备输出的'.format(device_number))


if __name__ == '__main__':
    cmd = AutoAdb()
    # 连接到设备
    cmd.run('connect 127.0.0.1:62001')
    device_str = cmd.run('devices')
    print(device_str)

    device_number_list = []
    for i in re.findall('(127.*?)	device', device_str, re.S | re.M):
        device_number_list.append(i)
        break

    for device_number in device_number_list:
        Process(target=start_device, args=(cmd, device_number)).start()
