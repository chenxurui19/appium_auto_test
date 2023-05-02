# -*- coding: utf-8 -*-
# @Time    : 2023/4/25 00:14
# @Author  : CXRui
# @File    : test_setting_wifi.py
# @Description :
import time
import pytest
import logging
from page.method.system.setting_method import SettingMethod

global setting


@pytest.mark.usefixtures("appium_setup")  # 引用conftest.py中的appium_setup方法，启动appium服务
@pytest.mark.usefixtures("driver_setup")  # 引用conftest.py中的driver_setup方法，创建会话
class TestSettingWifi:

    @pytest.fixture()
    def init_setup(self):
        global setting
        setting = SettingMethod(self.driver, self.platform)
        logging.info("前置：打开设置")
        setting.launch_setting()
        time.sleep(3)

        yield 1
        logging.info("后置：杀掉设置")
        setting.terminate_settting()

    @pytest.mark.test_setting_wifi
    def test_setting_wifi(self, init_setup):
        """
        测试用例案例：打开设置->点击进入WiFi界面->断言，判断是否进入WiFi界面
        :param init_setup: 前置条件 and 后置条件
        :return:
        """
        logging.info("测试：点击Wi-Fi,进入到Wi-Fi连接界面")
        setting.click_wifi_text()
        # 如果已经进入到Wi-Fi界面，但是判断控件找不到，即判定没有进入到Wi-Fi界面，可以用添加or继续判定更加准确，请同学们自由发挥。
        result = setting.check_network_text_status()
        assert result, "没有进入到Wi-Fi界面"





