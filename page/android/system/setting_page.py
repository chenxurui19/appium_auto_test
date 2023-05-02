# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 22:24
# @Author  : CXRui
# @File    : system.py
# @Description :
from appium.webdriver.common.mobileby import MobileBy


class SettingPage:
    # 进入wi-fi连接界面按钮
    wlan_text = (MobileBy.XPATH, '//android.widget.TextView[@text="WLAN" or @text="Wi-Fi"]')

    # 选取网络的文字，用来判断是否已进入选择Wi-Fi的页面
    network_text = (MobileBy.XPATH, '//android.widget.TextView[@text="选取网络"]')