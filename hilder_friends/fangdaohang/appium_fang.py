from appium import webdriver
import time
from lib.log import LogHandler
log = LogHandler(__name__)
desired_caps = {}
desired_caps['appPackage'] = 'com.lansi.fangdaohang'
desired_caps['appActivity'] = 'com.lansi.realtynavi.ui.guide.LogoActivity'
desired_caps['platformName'] = 'Android'
desired_caps['deviceName'] = '19a89ac67d15'
desired_caps['platformVersion'] = '7.1'
desired_caps['noReset'] = 'true'
driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)
time.sleep(3)
driver.find_element_by_xpath('(//android.widget.ImageView[@content-desc="icon"])[4]').click()
time.sleep(5)

def community_click():
    com_list = driver.find_elements_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.support.v4.widget.DrawerLayout/android.widget.RelativeLayout/android.widget.FrameLayout[1]/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.support.v7.widget.RecyclerView/android.widget.LinearLayout')
    for i in range(len(com_list)):
        try:
            com_list[i].click()
            time.sleep(2)
            driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.ScrollView/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.ImageView').click()
            time.sleep(2)
            co_name = driver.find_element_by_id('com.lansi.fangdaohang:id/tvTitle').text
            driver.find_element_by_id('com.lansi.fangdaohang:id/llyifangyijia').click()
            building_click(co_name)
            log.info('小区{}点击事件已完成'.format(co_name))
            driver.back()
        except Exception as e:
            log.error('小区点击事件失败={}'.format(e))
            continue

def building_click(co_name):
    latest_text = ''
    while True:
        try:
            els = driver.find_elements_by_id('com.lansi.fangdaohang:id/tvBuildLocation')
            for i in range(len(els)):
                els[i].click()
                driver.tap([(590,779)])
                driver.find_element_by_id('com.lansi.fangdaohang:id/llyifangyijia').click()
            present_text = els[0].text
            if present_text == latest_text:
                break
            else:
                latest_text = present_text
            driver.swipe(0,1232,0,864)
        except Exception as e:
            log.error('小区{}楼栋信息获取失败={}'.format(co_name,e))
            break
    driver.back()
    driver.back()


if __name__ == '__main__':
    while True:
        try:
            if '没有更多数据' in driver.page_source:
                break
            else:
                driver.swipe(400, 1130, 400, 250)
        except:
            driver.swipe(400, 1130, 400, 250)
    while True:
        time.sleep(2)
        community_click()
        driver.swipe(400,300,400,1130,)
        time.sleep(2)


