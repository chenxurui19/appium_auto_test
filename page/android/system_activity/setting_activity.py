# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 22:24
# @Author  : CXRui
# @File    : system_activity.py
# @Description :
from appium.webdriver.common.mobileby import MobileBy


class SettingActivity:
    # 进入wi-fi连接界面按钮
    wlan_text = (MobileBy.XPATH, "//android.widget.TextView[@text='WLAN']")
    wifi_text = (MobileBy.XPATH, "//android.widget.TextView[@text='Wi-Fi']")

    # wi-fi页面开关按钮
    wifi_switch = (MobileBy.XPATH, "//android.widget.LinearLayout[@resource-id='android:id/widget_frame']")
