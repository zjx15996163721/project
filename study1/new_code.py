import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 初始化
class GeetestSpider():
    def __init__(self):
        self.url = "https://i.flyme.cn/register"
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)

    def get_button(self):
        """
        获取初始验证按钮，模拟点击
        :return:按钮对象
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip_content')))
        return button

    def get_screen_image(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screen_img = self.browser.get_screenshot_as_png()
        screen_img = Image.open(BytesIO(screen_img))
        return screen_img

    def get_position(self):
        """
        获取验证码的位置
        :return: 验证码位置元祖
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return top, bottom, left, right

    def get_geetest_img(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象,Image对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置：', top, bottom, left, right)
        screen_img = self.get_screen_image()
        # 剪裁图片
        captcha = screen_img.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_slider(self):
        """
        获取滑块
        :return:滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def equal_rgb(self, img1, img2, x, y):
        """
        判断两个像素点是否相同
        :param img1: 图片1
        :param img2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 是否相同
        """
        # 获取两张图片的像素点
        pixel1 = img1.load()[x, y]
        pixel2 = img2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self, img1, img2):
        """
        获取偏移量
        :param img1:不带缺口的图片
        :param img2: 带缺口的图片
        :return: 偏移量
        """
        # 直接从滑块的右侧开始遍历
        left = 60
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.equal_rgb(img1, img2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, d):
        """
        根据偏移量获取运动轨迹
        :param d: 偏移量
        :return: 运动轨迹,每次移动距离
        """
        # 运动轨迹
        track = []
        # 当前位移
        current = 0
        # 开始减速的偏移量,设位移达到偏移量的2/3时开始减速
        deviation = d * 2 / 3
        # 　间隔时间
        t = 0.2
        # 初始速度
        v = 0

        while current < d:
            if current < deviation:
                # 加速阶段
                a = 2
            else:
                # 减速阶段
                a = -2

            # 初始速度
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 位移
            move = v0 * t + a * t * t / 2
            # 当前位移
            current += move
            # 添加到轨迹，保留整数
            track.append(round(move))
        return track

    def move_slider(self, slider, track):
        """
        按照轨迹移动滑块至缺口
        :param slider:滑块
        :param track: 轨迹
        :return:
        """
        # 鼠标按住滑块
        ActionChains(self.browser).click_and_hold(slider).perform()
        for i in track:
            # 遍历轨迹元素，每次移动对应位移
            ActionChains(self.browser).move_by_offset(xoffset=i, yoffset=0).perform()
        time.sleep(0.5)
        # 移动完成后，松开鼠标
        ActionChains(self.browser).release().perform()

    def crack(self):
        """
        模拟验证的各种操作
        :return:None
        """
        # 打开网站，输入注册手机号
        self.browser.get(self.url)
        self.wait.until(EC.presence_of_element_located((By.ID, 'phone')))
        # 点击验证
        button = self.get_button()
        button.click()


        # 获取验证码图片
        img1 = self.get_geetest_img('captcha1.png')
        # 获取滑块
        slider = self.get_slider()
        slider.click()
        # 获取带缺口的图片
        img2 = self.get_geetest_img('captcha2.png')
        # 获取缺口位置
        gap = self.get_gap(img1, img2)
        print("缺口位置：", gap)
        # 减去缺口位移
        gap -= 6
        # 获取轨迹
        track = self.get_track(gap)
        print("轨迹：", track)
        # 拖动滑块
        self.move_slider(slider, track)

        success = self.wait.until(
            EC.text_to_be_present_in_element((By.ID, 'geetest_success_radar_tip_content'), '验证成功'))

        # 失败重试
        if not success:
            self.crack()


if __name__ == '__main__':
    crack = GeetestSpider()
    crack.crack()