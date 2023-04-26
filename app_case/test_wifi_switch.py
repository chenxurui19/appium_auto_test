# -*- coding: utf-8 -*-
# @Time    : 2023/4/25 00:14
# @Author  : CXRui
# @File    : test_wifi_switch.py
# @Description :
import time
import pytest
import logging
from page.method.system_page.setting_page import SettingPage

global setting


@pytest.mark.usefixtures("appium_setup")  # 引用conftest.py中的appium_setup方法，启动appium服务
@pytest.mark.usefixtures("driver_setup")  # 引用conftest.py中的driver_setup方法，创建会话
class Test1:

    @pytest.fixture()
    def init_setup(self):
        global setting
        setting = SettingPage(self.driver, self.platform)
        logging.info("前置：打开设置")
        setting.launch_setting()
        time.sleep(3)

        yield 1
        logging.info("后置：杀掉设置")
        setting.terminate_settting()

    @pytest.mark.test_1
    def test_1(self, init_setup):
        logging.info("测试：打开Wi-Fi界面")
        setting.click_wifi_text()
        time.sleep(3)
        if setting.get_wifi_status():
            logging.info("测试：关闭Wi-Fi开关按钮")
            # iPhone的Wi-Fi开关容易点击不到，建议用坐标进行点击
            setting.click_wifi_switch()
            time.sleep(3)
            assert not setting.get_wifi_status(), "关闭失败"
        logging.info("测试：打开Wi-Fi开关按钮")
        # iPhone的Wi-Fi开关容易点击不到，建议用坐标进行点击
        setting.click_wifi_switch()
        time.sleep(3)
        assert setting.get_wifi_status(), "打开失败"




