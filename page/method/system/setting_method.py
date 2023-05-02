# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 22:25
# @Author  : CXRui
# @File    : setting_method.py
# @Description :
from ..base_method import BaseMethod
from config.config import GlobalVar
from selenium.common.exceptions import NoSuchElementException
global LOCATOR


class SettingMethod(BaseMethod):
    def __init__(self, driver, platform):
        global LOCATOR
        super().__init__(driver, platform)
        if platform == GlobalVar.IOS:
            from page.ios.system.setting_page import SettingPage
        else:
            from page.android.system.setting_page import SettingPage
        LOCATOR = SettingPage()

    def click_wifi_text(self):
        """
        进入Wi-Fi选择页面
        :return:
        """
        try:
            self.click_element(LOCATOR.wifi_text)
        except NoSuchElementException as e:
            self.click_element(LOCATOR.wlan_text)

    def check_network_text_status(self):
        """
        判断“网络”/“选取网络”文字是否存在，依此判断是否进入到Wi-Fi界面
        :return:
        """
        return self.is_exist(LOCATOR.network_text)
