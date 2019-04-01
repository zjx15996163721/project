from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options

# 设置代理
proxy = '127.0.0.1:8080'
chrome_options = Options()
chrome_options.add_argument('--proxy-server={0}'.format(proxy))
# 不显示网页,无头chrome
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=chrome_options)
# 设置最大分辨率, 与无头chrome二选一
# browser.maximize_window()
"""
登录页面
"""
# 打开网页
browser.get('http://res.hhhuo.net/login')
# 获取第一个输入框，输入电话
input_phone = browser.find_element_by_xpath('//*[@id="res"]/section/main/div[2]/form/div[1]/div[1]/div[1]/input')
input_phone.send_keys('13918530594')

# 输入验证码
verification_button = browser.find_element_by_xpath('//*[@id="res"]/section/main/div[2]/form/div[2]/div[1]/button')
verification_button.click()
time.sleep(2)
verification = input('请输入验证码:')
# 获取第二个输入框，输入验证码
input_verification = browser.find_element_by_xpath('//*[@id="res"]/section/main/div[2]/form/div[2]/div/div/input')
input_verification.send_keys(verification)
# 点击登录
login_button = browser.find_element_by_xpath('//*[@id="res"]/section/main/div[2]/form/div[3]/div[1]/button')
login_button.click()
print('登录成功')
# 等待页面加载完成
time.sleep(2)

"""
二手成交
"""


def start_second():
    """
    登录之后页面
    """
    # 点击 三级市场
    browser.get('http://res.hhhuo.net/index')
    # 等待页面加载完成
    time.sleep(10)
    third_bazaar_button = browser.find_element_by_xpath('//*[@id="menu"]/ul/li[5]/div')
    third_bazaar_button.click()
    # 等待页面加载完成
    time.sleep(2)
    # 点击 二手房成交
    second_deal_button = browser.find_element_by_xpath('//*[@id="menu"]/ul/li[5]/ul/li[1]')
    second_deal_button.click()
    # 等待页面加载完成
    time.sleep(2)
    # 输入查询日期
    start_date_input = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[1]/div[1]/form/div/div[1]/div/div[1]/input')
    start_date_input.clear()
    start_date = input('请输入二手成交起始日期：')
    start_date_input.send_keys(start_date)

    end_date_input = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[1]/div[1]/form/div/div[1]/div/div[2]/input')
    end_date_input.clear()
    end_date = input('请输入二手成交结束日期：')
    end_date_input.send_keys(end_date)

    # 查询
    inquire_button = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[2]/div[2]/button')
    inquire_button.click()
    print('查询成功')
    # 等待页面加载完成
    time.sleep(2)
    page_num = 1
    # 点击下一页
    while True:
        next_page_button = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[3]/div/div[3]/div/button[2]')
        next_page_button.click()
        page_num += 1
        print('点击第{}页'.format(page_num))
        # 模拟人的行为,延迟点击
        time.sleep(2)
        # 翻页到最后,判断元素属性是否为disabled,是否可点击
        flag = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[3]/div/div[3]/div/button[2]').get_attribute('disabled')
        if flag is not None:
            break
    print('二手成交点击事件完成')
    # 关闭浏览器
    browser.close()
    print('点击事件完成,关闭浏览器')


"""
新房成交
"""


def start_new_house():

    """
    登录之后页面
    """
    # 点击 二级市场
    browser.get('http://res.hhhuo.net/index')
    # 等待页面加载完成
    time.sleep(10)
    third_bazaar_button = browser.find_element_by_xpath('//*[@id="menu"]/ul/li[4]/div')
    third_bazaar_button.click()
    # 等待页面加载完成
    time.sleep(2)
    # 点击 新房成交
    second_deal_button = browser.find_element_by_xpath('//*[@id="menu"]/ul/li[4]/ul/li[1]')
    second_deal_button.click()
    # 等待页面加载完成
    time.sleep(2)
    # 输入查询日期
    start_date_input = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[1]/div[1]/form/div/div[1]/div/div[1]/input')
    start_date_input.clear()
    start_date = input('请输入新房成交起始日期：')
    start_date_input.send_keys(start_date)

    end_date_input = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[1]/div[1]/form/div/div[1]/div/div[2]/input')
    end_date_input.clear()
    end_date = input('请输入新房成交结束日期：')
    end_date_input.send_keys(end_date)

    # 查询
    inquire_button = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[2]/div[2]/button')
    inquire_button.click()
    print('查询成功')
    # 等待页面加载完成
    time.sleep(2)
    page_num = 1
    # 点击下一页
    while True:
        next_page_button = browser.find_element_by_xpath('//*[@id="newlist"]/div/div[3]/div/button[2]')
        next_page_button.click()
        page_num += 1
        print('点击第{}页'.format(page_num))
        # 模拟人的行为,延迟点击
        time.sleep(2)
        # 翻页到最后,判断元素属性是否为disabled,是否可点击
        flag = browser.find_element_by_xpath('//*[@id="newlist"]/div/div[3]/div/button[2]').get_attribute('disabled')
        if flag is not None:
            break
    print('新房成交点击事件完成')
    # 关闭浏览器
    browser.close()
    print('点击事件完成,关闭浏览器')


"""
土地成交
"""


def start_land():

    """
    登录之后页面
    """
    # 点击 一级市场
    browser.get('http://res.hhhuo.net/index')
    # 等待页面加载完成
    time.sleep(10)
    third_bazaar_button = browser.find_element_by_xpath('//*[@id="menu"]/ul/li[3]/div')
    third_bazaar_button.click()
    # 等待页面加载完成
    time.sleep(2)
    # 点击 土地
    second_deal_button = browser.find_element_by_xpath('//*[@id="menu"]/ul/li[3]/ul/li[1]')
    second_deal_button.click()
    # 等待页面加载完成
    time.sleep(2)
    # 输入查询日期
    start_date_input = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[1]/div[1]/form/div/div[1]/div/div[1]/input')
    start_date_input.clear()
    start_date = input('请输入土地成交起始日期：')
    start_date_input.send_keys(start_date)

    end_date_input = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[1]/div[1]/form/div/div[1]/div/div[2]/input')
    end_date_input.clear()
    end_date = input('请输入土地成交结束日期：')
    end_date_input.send_keys(end_date)

    # 查询
    inquire_button = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[2]/div[2]/button[1]')
    inquire_button.click()
    print('查询成功')
    # 等待页面加载完成
    time.sleep(2)
    page_num = 1
    # 点击下一页
    while True:
        next_page_button = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[3]/div/div[2]/div/button[2]')
        next_page_button.click()
        page_num += 1
        print('点击第{}页'.format(page_num))
        # 模拟人的行为,延迟点击
        time.sleep(2)
        # 翻页到最后,判断元素属性是否为disabled,是否可点击
        flag = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3]/div/div/div[3]/div/div[2]/div/button[2]').get_attribute('disabled')
        if flag is not None:
            break
    print('土地成交点击事件完成')
    # 关闭浏览器
    browser.close()
    print('点击事件完成,关闭浏览器')

