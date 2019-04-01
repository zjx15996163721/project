import random
import time
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import requests
from io import BytesIO


class Verification:

    def __init__(self):
        self.driver = webdriver.Chrome()

    def visit_index(self):
        self.driver.get('http://www.sgs.gov.cn/notice/')
        self.driver.find_element_by_id("keyword").send_keys('中国长城工业上海有限公司')
        WebDriverWait(self.driver, 10, 0.5).until(
            EC.element_to_be_clickable((By.ID, 'buttonSearch')))

        self.driver.find_element_by_id('buttonSearch').click()

        WebDriverWait(self.driver, 10, 0.5).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="gt_slider_knob gt_show"]')))

        # 模拟拖动
        self.analog_drag()

    def analog_drag(self):
        # 鼠标移动到拖动按钮，显示出拖动图片
        element = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
        ActionChains(self.driver).move_to_element(element).perform()
        time.sleep(3)

        # 刷新验证码
        self.driver.find_element_by_xpath('//a[@class="gt_refresh_button"]').click()
        time.sleep(1)
        # 获取图片地址和位置坐标列表
        cut_image_url, cut_location = self.get_image_url('//div[@class="gt_cut_bg_slice"]')
        full_image_url, full_location = self.get_image_url('//div[@class="gt_cut_fullbg_slice"]')

        # 根据坐标拼接图片
        cut_image = self.mosaic_image(cut_image_url, cut_location)
        full_image = self.mosaic_image(full_image_url, full_location)

        # 保存图片
        cut_image.save("cut.jpg")
        full_image.save("full.jpg")

        # 根据两个图片计算距离
        distance = self.get_offset_distance(cut_image, full_image)

        # 开始移动
        self.start_move(distance)

        # 如果出现error
        try:
            WebDriverWait(self.driver, 5, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="gt_ajax_tip gt_error"]')))
            print("验证失败")
            return
        except TimeoutException as e:
            pass

        # 判断是否验证成功
        s = self.driver.find_elements_by_xpath('//*[@id="wrap1"]/div[3]/div/div/p')
        if len(s) == 0:
            print("滑动解锁失败,继续尝试")
            self.analog_drag()
        else:
            print("滑动解锁成功")
            time.sleep(1)
            ss = self.driver.find_element_by_xpath('//*[@id="wrap1"]/div[3]/div/div/div[2]').get_attribute("onclick")
            print(ss)
            ss = self.driver.find_element_by_xpath('//*[@id="wrap1"]/div[3]/div/div/div[2]').click()

    # 获取图片和位置列表
    def get_image_url(self, xpath):
        link = re.compile('background-image: url\("(.*?)"\); background-position: (.*?)px (.*?)px;')
        elements = self.driver.find_elements_by_xpath(xpath)
        image_url = None
        location = []
        for element in elements:
            style = element.get_attribute("style")
            groups = link.search(style)
            url = groups[1]
            x_pos = groups[2]
            y_pos = groups[3]
            location.append((int(x_pos), int(y_pos)))
            image_url = url
        return image_url, location

    # 拼接图片
    def mosaic_image(self, image_url, location):
        r = requests.get(image_url)
        file = BytesIO(r.content)
        img = Image.open(file)
        image_upper_lst = []
        image_down_lst = []
        for pos in location:
            if pos[1] == 0:
                # y值==0的图片属于上半部分，高度58
                # 一张张小图片
                image_upper_lst.append(img.crop((abs(pos[0]), 0, abs(pos[0]) + 10, 58)))
            else:
                # y值==58的图片属于下半部分
                # 一张张小图片
                image_down_lst.append(img.crop((abs(pos[0]), 58, abs(pos[0]) + 10, img.height)))

        # 将小图片重新拼凑起来
        x_offset = 0
        # 创建一张画布，x_offset主要为新画布使用
        new_img = Image.new("RGB", (260, img.height))
        for img in image_upper_lst:
            new_img.paste(img, (x_offset, 58))
            x_offset += img.width

        x_offset = 0
        for img in image_down_lst:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width

        return new_img

    # 计算距离
    def get_offset_distance(self, cut_image, full_image):
        for x in range(cut_image.width):
            for y in range(cut_image.height):
                cpx = cut_image.getpixel((x, y))
                fpx = full_image.getpixel((x, y))
                if not self.is_similar_color(cpx, fpx):
                    img = cut_image.crop((x, y, x + 50, y + 40))
                    # 保存一下计算出来位置图片，看看是不是缺口部分
                    img.save("1.jpg")
                    return x

    # 判断颜色是否相近
    def is_similar_color(self, x_pixel, y_pixel):
        for i, pixel in enumerate(x_pixel):
            if abs(y_pixel[i] - pixel) > 50:
                return False
        return True

    # 开始移动
    def start_move(self, distance):
        element = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')

        # 这里就是根据移动进行调试，计算出来的位置不是百分百正确的，加上一点偏移
        distance -= element.size.get('width') / 2
        distance += 15

        # 按下鼠标左键
        ActionChains(self.driver).click_and_hold(element).perform()
        time.sleep(0.5)
        while distance > 0:
            if distance > 10:
                # 如果距离大于10，就让他移动快一点
                span = random.randint(5, 8)
            else:
                # 快到缺口了，就移动慢一点
                span = random.randint(2, 3)
            ActionChains(self.driver).move_by_offset(span, 0).perform()
            distance -= span
            time.sleep(random.randint(10, 50) / 100)

        ActionChains(self.driver).move_by_offset(distance, 1).perform()
        # 释放鼠标
        ActionChains(self.driver).release(on_element=element).perform()


if __name__ == '__main__':
    v = Verification()
    v.visit_index()

