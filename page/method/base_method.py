# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 22:28
# @Author  : CXRui
# @File    : base_method.py
# @Description : Appium二次封装
import os
import time
from config.config import GlobalVar
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BaseMethod:
    def __init__(self, driver, platform):
        self.driver = driver
        self.platform = platform

    def open_app(self):
        """
        打开app
        :return:
        """
        self.driver.launch_app()

    def close_app(self):
        """
        关闭app
        :return:
        """
        self.driver.close_app()

    def restart_app(self):
        """
        重启app
        :return:
        """
        self.driver.reset()

    def press_back(self):
        """
        点击返回
        :return:
        """
        if self.platform == GlobalVar.IOS:
            self.driver.execute_script("mobile: pressButton", {"name": "home"})
        else:
            self.driver.press_keycode(4)

    def press_home(self):
        """
        点击home
        :return:
        """
        if self.platform == GlobalVar.IOS:
            self.driver.execute_script("mobile: pressButton", {"name": "home"})
        else:
            self.driver.press_keycode(3)

    def long_click_element(self, locator, index=0, duration=2000):
        """
        长按
        :param locator:
        :param index:
        :param duration:
        :return:
        """
        el = self.get_element(locator, index)
        att, scroll = self.get_element_attributes(el)
        x = att['center_x']
        y = att['center_y']
        if self.platform == GlobalVar.ANDROID:
            self.tap(x, y, duration)
        else:
            duration = duration / 1000
            self.driver.execute_script("mobile: dragFromToForDuration",
                                       {"fromX": x, "fromY": y, "toX": x, "toY": y, "duration": duration})
        return el

    def get_element(self, locator, index=0):
        """
        获取控件
        :param locator:
        :return:
        """
        method = locator[0]
        values = locator[1]
        if index == 0:
            el = self.get_element_by_type(method, values)
        elif index > 0:
            el = self.get_elements_by_type(method, values)[index]
        else:
            els = self.get_elements_by_type(method, values)
            el = els[len(els)+index]
        return el

    def click_element(self, locator, index=0):
        """
        点击控件
        :param locator:
        :param index:
        :return:
        """
        el = self.get_element(locator, index)
        el.click()
        return el

    def get_element_by_type(self, method, value):
        msg = 'selenium.common.exceptions.NoSuchElementException:' \
              ' ("{}", "{}") could not be located on the page using the given search parameters.'.format(method, value)
        locator = (method, value)
        # 每次查找元素最多等待10s，每隔0.5s查找一次
        try:
            el = WebDriverWait(self.driver, 10, 0.5).until(
                EC.visibility_of_element_located(locator), msg.format(value))
        except TimeoutException:
            el = self.driver.find_element(method, value)
        return el

    def get_elements_by_type(self, method, value):
        msg = 'selenium.common.exceptions.NoSuchElementException:' \
              ' ("{}", "{}") could not be located on the page using the given search parameters.'.format(method, value)
        locator = (method, value)
        # 每次查找元素最多等待10s，每隔0.5s查找一次
        try:
            WebDriverWait(self.driver, 10, 0.5).until(
                EC.visibility_of_element_located(locator), msg.format(value))
        except TimeoutException as e:
            print(e)
        return self.driver.find_elements(method, value)

    def get_elements(self, locator):
        """
        获取满足条件的所有控件
        :param locator:
        :return:
        """
        method = locator[0]
        values = locator[1]
        if type(values) is str:
            return self.get_elements_by_type(method, values)
        elif type(values) is list:
            for value in values:
                try:
                    return self.get_elements_by_type(method, value)
                except (TimeoutException, NoSuchElementException) as e:
                    print(e)
            raise NoSuchElementException

    def get_text(self, locator, index=0):
        """
        获取字符串
        :param locator:
        :return:
        """
        el = self.get_element(locator, index)
        return el.text

    def is_exist(self, *locator, index=0):
        """
        控件是否存在，返回的第二个值是控件对象或者None，当flag为True时，直接拿到item对其进行点击等操作，不再调用一次查找控件，以此减少重复请求查找控件，加快脚本执行速度
        :param locator:
        :return:
        """
        for loc in locator:
            try:
                item = self.get_element(loc, index)
            except (TimeoutException, NoSuchElementException) as e:
                print(e)
            else:
                if self.platform == GlobalVar.ANDROID:  # 对于android平台来说，能拿到控件，控件就是对用户可见的
                    return item
                elif item.is_displayed():  # 对于ios来说，能拿到控件不一定是对用户可见的，需要用is_displayed()判断一下
                    return item
        return False

    def is_exist_click(self, *locator, index=0):
        """
        如果控件存在，则点击
        :param locator:
        :param index:
        :return:
        """
        el = None
        if self.is_exist(*locator, index=index):
            el = self.click_element(*locator)
        return el

    def is_text_exist(self, text):
        """
        字符串是否存在
        :param text:
        :return:
        """

        def wait_text(self, text, timeout=10):
            if self.platform == GlobalVar.ANDROID:
                locator = (MobileBy.ANDROID_UIAUTOMATOR, f'text("{text}")')
            else:
                locator = (MobileBy.NAME, text)
            try:
                element = WebDriverWait(self.driver, timeout, 0.1).until(
                    EC.presence_of_element_located(locator))
            except (TimeoutException, NoSuchElementException):
                return False
            if element:
                return element
            return False

    def wait_to_visibility(self, locator, timeout=10):
        """
        等待控件出现
        :param locator:
        :param timeout:
        :return:
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator))
        except (TimeoutException, NoSuchElementException):
            return False
        if element:
            return element
        return False

    def wait_to_not_visibility(self, locator, timeout=10):
        """
        等待控件消失
        :param locator:
        :param timeout:
        :return:
        """
        try:
            element = WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located(locator))
        except (TimeoutException, NoSuchElementException):
            return False
        return element

    def wait_not_exist(self, locator, timeout=10, poll_frequency=0.5):
        """
        等待存在的控件消失
        :param locator:
        :param timeout:
        :return:
        """
        try:
            # WebDriverWait(self.driver, timeout).until_not(
            #     EC.presence_of_element_located(locator))
            el = WebDriverWait(self.driver, timeout, poll_frequency=poll_frequency).until(
                EC.invisibility_of_element_located(locator))
        except (TimeoutException, NoSuchElementException):
            return False
        return el

    def wait_elements(self, timeout=10, *locator):
        """
        等待多个控件之中的一个出现
        :param timeout:
        :param locator:
        :return:
        """
        end = time.time() + timeout
        while True:
            if time.time() > end:
                return False
            else:
                for loc in locator:
                    try:
                        el = self.driver.find_element(loc[0], loc[1])
                    except NoSuchElementException:
                        pass
                    else:
                        return el
                time.sleep(0.5)

    def read_toast(self, message):
        """
        读取toast信息文本
        """
        if self.platform == GlobalVar.ANDROID:
            toast_element = (MobileBy.XPATH, '//*[contains(@text,"%s")]' % message)
        else:
            toast_element = (MobileBy.XPATH, f'//*[contains(@name, "{message}")]')
            # toast_element = (MobileBy.NAME, message)
        toast = WebDriverWait(self.driver, 10, 0.1).until(EC.presence_of_element_located(toast_element))
        return toast.text

    def send_keys(self, locator, text, times=10, index=0):
        """
        带检查的文本输入，保证输入的字符串无误
        :param locator:
        :param text:
        :return:
        """
        if isinstance(locator, tuple):
            el = self.get_element(locator, index)
        else:
            el = locator
        for i in range(times):
            if el.text == text:
                return el
            el.clear()
            el.send_keys(text)
        if el.text == text:
            return el
        else:
            return None

    def swipe(self, start_x, start_y, end_x, end_y, duration):
        """
        重写swipe方法，主要解决框架里的swipe函数在ios平台不起作用的问题
        :param start_x:
        :param start_y:
        :param end_x:
        :param end_y:
        :param duration:
        :return:
        """
        if self.platform == GlobalVar.ANDROID:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        else:
            if not duration or duration < 500:
                duration = 0.5
            else:
                duration = duration / 1000
            self.driver.execute_script("mobile: dragFromToForDuration",
                                       {"fromX": start_x, "fromY": start_y, "toX": end_x, "toY": end_y,
                                        "duration": duration})

    def swipe_by_element(self, direction, start, end, percent, locator=None, duration=None):
        """
        滑动
        :param direction: 方向
        :param start: 起点相对（控件/屏幕）位置
        :param end: 终点相对（控件/屏幕）位置
        :param percent: 整体滑动在屏幕的位置
        :param locator: 控件，如不指定则是整个屏幕
        :param duration: 时长
        :return:
        """
        scroll = None
        if locator is None:
            window_size = self.driver.get_window_size()
            x = 0
            y = 0
            width = window_size['width']
            height = window_size['height']
        else:
            att = self.get_element_attributes(locator)
            x = att['left']
            y = att['top']
            width = att['width']
            height = att['height']
        if direction == 'up' or direction == 'down':
            start_x = x * (float(percent) + 1)
            start_y = y + float(float(start) * float(height))
            end_y = y + float(float(end) * float(height))
            self.swipe(start_x, start_y, start_x, end_y, duration)
        elif direction == 'left' or direction == 'right':
            start_x = x + float(start * width)
            end_x = x + float(end * width)
            start_y = y + float(percent * height)
            self.swipe(start_x, start_y, end_x, start_y, duration)

    def swipe_by_element(self, direction, start, end, percent, locator=None, duration=None):
        """
        滑动
        :param direction: 方向
        :param start: 起点相对（控件/屏幕）位置
        :param end: 终点相对（控件/屏幕）位置
        :param percent: 整体滑动在屏幕的位置
        :param locator: 控件，如不指定则是整个屏幕
        :param duration: 时长
        """
        scroll = None
        if locator is None:
            window_size = self.driver.get_window_size()
            x = 0
            y = 0
            width = window_size['width']
            height = window_size['height']
        else:
            att = self.get_element_attributes(locator)
            x = att['left']
            y = att['top']
            width = att['width']
            height = att['height']
        if direction == 'up' or direction == 'down':
            start_x = x * (float(percent) + 1)
            start_y = y + float(float(start) * float(height))
            end_y = y + float(float(end) * float(height))
            self.swipe(start_x, start_y, start_x, end_y, duration)
        elif direction == 'left' or direction == 'right':
            start_x = x + float(start * width)
            end_x = x + float(end * width)
            start_y = y + float(percent * height)
            self.swipe(start_x, start_y, end_x, start_y, duration)

    def launch_setting(self):
        """
        打开系统设置页，注意每台Android各有千秋
        :return:
        """
        if GlobalVar.get_test_platform() == 'android':
            # https://www.cnblogs.com/candyzhmm/p/11427960.html
            cmd = "adb -s {} shell am start com.android.settings/com.android.settings.Settings".\
                format(GlobalVar.get_device_sn())
            os.system(cmd)
        else:
            self.driver.execute_script("mobile:terminateApp", {"bundleId": "com.apple.Preferences"})
            time.sleep(3)
            self.driver.execute_script("mobile:launchApp", {"bundleId": "com.apple.Preferences"})

    def terminate_settting(self):
        if GlobalVar.get_test_platform() == 'android':
            pass
        else:
            self.driver.execute_script("mobile:terminateApp", {"bundleId": "com.apple.Preferences"})

    def adb_command(self, command):
        """
        支持Android adb的shell指令
        :param command:
        :return:
        """
        udid = GlobalVar.get_device_sn()
        os.system(f'adb -s {udid} shell {command}')

    def open_wifi(self):
        """
        打开wifi
        :return:
        """
        self.adb_command('svc wifi enable')

    def close_wifi(self):
        """
        关闭wifi
        :return:
        """
        self.adb_command('svc wifi disable')

    def tap_middle(self):
        """
        点击屏幕正中央
        :return:
        """
        udid = GlobalVar.get_device_sn()
        x = self.driver.get_window_size()['width']
        y = self.driver.get_window_size()['height']
        if GlobalVar.get_test_platform() == 'android':
            cmd = f'adb -s {udid} shell input tap {x/2} {y/2}'
            os.system(cmd)
        else:
            self.tap(x/2, y/2)

    def long_click_middle(self, duration=3000):
        """
        长按屏幕正中央
        :return:
        """
        x = self.driver.get_window_size()['width'] / 2
        y = self.driver.get_window_size()['height'] / 2
        if GlobalVar.get_test_platform() == 'android':
            os.system(f'adb -s {GlobalVar.get_device_sn()} shell input swipe {x} {y} {x} {y} {duration}')
        else:
            duration = duration / 1000
            self.driver.execute_script("mobile: dragFromToForDuration",
                                       {"fromX": x, "fromY": y, "toX": x, "toY": y, "duration": duration})

    def get_attribute(self, locator, name="text"):
        """
        获取控件属性值
        :param index:
        :param locator:
        :param name: 属性名
        :return:
        """
        return self.get_element(locator, 0).get_attribute(name)

    def get_cmd_result(self, cmd):
        import subprocess
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8').communicate()[0].strip()
        return p
