from selenium import webdriver
import time
from lxml import etree
browser = webdriver.Chrome()

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
time.sleep(5)
verification = input('请输入验证码:')
# 获取第二个输入框，输入验证码
input_verification = browser.find_element_by_xpath('//*[@id="res"]/section/main/div[2]/form/div[2]/div[1]/div[1]/input')
input_verification.send_keys(verification)
# 点击登录
login_button = browser.find_element_by_xpath('//*[@id="res"]/section/main/div[2]/form/div[3.png]/div[1]/button')
login_button.click()

"""
登录之后页面
"""
# 点击 三级市场
browser.get('http://res.hhhuo.net/index')
third_bazaar_button = browser.find_element_by_xpath('//*[@id="menu"]/ul/li[5]/div')
third_bazaar_button.click()
# 点击 二手房成交
second_deal_button = browser.find_element_by_xpath('//*[@id="menu"]/ul/li[5]/ul/li[1]')
second_deal_button.click()
# 输入查询日期
start_date_input = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3.png]/div/div/div[1]/div[1]/form/div/div[1]/div/div[1]/input')
start_date_input.clear()
start_date = input('请输入起始日期：')
start_date_input.send_keys(start_date)

end_date_input = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3.png]/div/div/div[1]/div[1]/form/div/div[1]/div/div[2]/input')
end_date_input.clear()
end_date = input('请输入结束日期：')
end_date_input.send_keys(end_date)

# 查询
inquire_button = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3.png]/div/div/div[2]/div[2]/button')
inquire_button.click()
time.sleep(5)

# 选取 100条每页
# quantity_button = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3.png]/div/div/div[3.png]/div/div[3.png]/div/span[2]/div/div/input')
# quantity_button.click()
# one_hundred_button = browser.find_element_by_xpath("/html/body/div[10]/div[1]/div[1]/ul/li[4]/span")
# one_hundred_button.click()

# 点击下一页
while True:
    next_page_button = browser.find_element_by_xpath('//*[@id="res"]/section/section/main/div/div[2]/div[3.png]/div/div/div[3.png]/div/div[3.png]/div/button[2]')
    next_page_button.click()
