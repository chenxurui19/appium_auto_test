# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 22:25
# @Author  : CXRui
# @File    : setting_activity.py
# @Description :
from appium.webdriver.common.mobileby import MobileBy


class SettingActivity:
    # 点击Wi-Fi页面按钮
    wifi_text = (MobileBy.NAME, "Wi-Fi")

    # Wi-Fi的Switch开关
    wifi_switch = (MobileBy.XPATH, "//XCUIElementTypeSwitch[@name='Wi‑Fi']")
