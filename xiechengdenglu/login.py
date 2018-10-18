#coding=utf-8
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import Chaojiying
username = '********'  #携程账号和密码
password = '********'
CHAOJIYING_USERNAME = '********'  #超级鹰的账号和密码
CHAOJIYING_PASSWORD = '********'
CHAOJIYING_SOFT_ID = 897338
CHAOJIYING_KIND = 9004

class login():
    def __init__(self):
        self.url = 'https://passport.ctrip.com/user/login?BackUrl=http%3A%2F%2Fwww.ctrip.com%2F#ctm_ref=c_ph_login_buttom'
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 20)
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)

    def loginto(self):
        """
        登录起始页
        用户名和密码输入
        :return:
        """
        self.driver.get(self.url)
        user = self.driver.find_element_by_id('nloginname')
        user.send_keys(username)            #输入用户名
        passw = self.driver.find_element_by_id('npwd')
        passw.send_keys(password)           #输入密码
        slider = self.get_slider()          #获取滑块位置
        track = self.get_track(300)         #获取滑动轨迹
        self.move_to_gap(slider, track)     #开始滑动
        image = self.get_touclick_image()   #获取点击图片
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')
        #利用超级鹰识别验证码,result为返回结果
        result = self.chaojiying.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)
        locations = self.get_points(result)
        self.touch_click_words(locations)  #点击验证
        self.touch_click_verify()          #点击后提交
        self.logint()                      #点击登录


    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'cpt-drop-btn')))
        return slider

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def logint(self):
        self.driver.find_element_by_id('nsubmit').click()

    def get_touclick_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="sliderddnormal-choose"]/div[2]')))
        return element

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        element = self.get_touclick_element()
        time.sleep(2)
        location = element.location
        size = element.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        top = int(top)
        bottom = int(bottom)
        left = int(left)
        right = int(right)
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_touclick_image(self, name='captch.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_points(self, captcha_result):
        """
        解析识别结果
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def touch_click_words(self, locations):
        """
        点击验证图片
        :param locations: 点击位置
        :return: None
        """
        for location in locations:
            print(location)
            ActionChains(self.driver).move_to_element_with_offset(self.get_touclick_element(), location[0],
                                                                   location[1]).click().perform()
            time.sleep(1)

    def touch_click_verify(self):
        """
        点击验证按钮
        :return: None
        """
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="cpt-sub-box"]/a')))
        button.click()


if __name__ == '__main__':
    lo = login()
    lo.loginto()


