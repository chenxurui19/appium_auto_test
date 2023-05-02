# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 22:25
# @Author  : CXRui
# @File    : setting_page.py
# @Description :
from appium.webdriver.common.mobileby import MobileBy


class SettingPage:
    # 点击Wi-Fi页面按钮
    wifi_text = (MobileBy.NAME, "Wi-Fi")

    # 选取网络的文字，用来判断是否已进入选择Wi-Fi的页面
    network_text = (MobileBy.XPATH, '//XCUIElementTypeStaticText[@name="网络"]')
