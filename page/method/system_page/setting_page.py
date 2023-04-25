# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 22:25
# @Author  : CXRui
# @File    : setting_page.py
# @Description :
from ..base_method import BaseMethod
from config.config import GlobalVar
from selenium.common.exceptions import NoSuchElementException
global LOCATOR


class SettingPage(BaseMethod):
    def __init__(self, driver, platform):
        global LOCATOR
        super().__init__(driver, platform)
        if platform == GlobalVar.IOS:
            from page.ios.system_activity.setting_activity import SettingActivity
        else:
            from page.android.system_activity.setting_activity import SettingActivity
        LOCATOR = SettingActivity()

    def click_wifi_text(self):
        """
        进入Wi-Fi选择页面
        :return:
        """
        try:
            self.click_element(LOCATOR.wifi_text)
        except NoSuchElementException as e:
            self.click_element(LOCATOR.wlan_text)

    def click_wifi_switch(self):
        """
        点击Wi-Fi的Switch开关
        :return:
        """
        self.click_element(LOCATOR.wifi_switch)

    def get_wifi_status(self):
        """
        获取Wi-Fi的开关状态
        :return:
        """
        result = self.get_cmd_result("adb shell dumpsys wifi | grep Wi-Fi")
        if "Wi-Fi is enabled" in result:
            return True
        else:
            return False

