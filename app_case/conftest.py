# -*- coding: utf-8 -*-
# @Time    : 2023/4/24 19:12
# @Author  : CXRui
# @File    : conftest.py
# @Description : pytest特有的测试配置文件，可以理解成一个专门放fixture(设备、工具)的地方
import logging
import os.path
import sys
import subprocess
import pytest
import datetime
from util import util
from config.config import GlobalVar
import time
import signal
from appium import webdriver

src = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
server_ip = "127.0.0.1"  # appium服务运行的ip，一般appium服务和脚本都在同一台电脑上执行，使用'127.0.0.1'不需要修改
appium_port = 4723  # appium服务监听的端口，4723是初始值，执行过程中由脚本随机分配一个空闲端口，不需要人工介入
wda_port = 8100  # webdriveragent服务监听的端口，8100是初始值，执行过程中由脚本随机分配一个空闲端口，不需要人工介入
system_port = 8200  # adb转发端口，8200是初始值，执行过程中由脚本随机分配一个空闲端口，不需要人工介入
device_sn = ""  # 手机sn号，脚本从执行命令中读取后重新赋值
appium_p = None
driver = None
platform = ""  # 手机平台，android或ios
date_format = '%Y-%m-%d_%H.%M.%S'
rp_logger = None

"""
1、-session：顶层的fixture,该目录下所有的测试文件执行前会执行一次，只执行一次。
2、-module：模块级别的fixture，该目录下每个测试文件执行前都会执行一次。
3、-class：类级别的fixture，该目录下每个测试类执行前会执行一次
4、function：方法级别的fixture，每个方法执行前 都会执行一次。
"""


@pytest.fixture(scope="session")
def appium_setup(request):
    global device_sn, platform, appium_port, device_name, platform_version, wda_port, system_port, appium_port

    GlobalVar.set_device_sn(device_sn(request))
    GlobalVar.set_bundle_id(bundle_id(request))
    GlobalVar.set_app_activity(app_activity(request))

    appium_log_dir = f"{src}/appium_log/"  # appium_log文件夹，如不存在就创建
    if not os.path.exists(appium_log_dir):
        os.makedirs(appium_log_dir)

    pytest_log_dir = f"{src}/pytest_log/"
    if not os.path.exists(pytest_log_dir):
        os.makedirs(pytest_log_dir)

    report_dir = f"{src}/html_report/"  # html_report文件夹，如不存在就创建
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    appium_port = util.create_port(server_ip, 4723, 7999)  # 创建空闲的appium端口号
    appium_log_path = "{}{}_{}.log".format(appium_log_dir, datetime.datetime.now().strftime(date_format),
                                           appium_port)  # appium log存放的位置

    # 如果手机的设备号大于20，则为ios设备，否则为android
    if len(GlobalVar.get_device_sn()) > 20:
        platform = GlobalVar.IOS
        GlobalVar.set_test_platform(platform)
        wda_port = util.create_port(server_ip, 8100, 9999)  # 创建空闲的wda端口号
        device_name = util.get_iphone_name(GlobalVar.get_device_sn())
        platform_version = util.get_iphone_version(GlobalVar.get_device_sn())
        appium_p = subprocess.Popen(
            "appium -a {} -p {} --webdriveragent-port {} --relaxed-security "
            "--session-override --no-reset> {} 2>&1 &"
            .format(server_ip, appium_port, wda_port, appium_log_path), stdout=subprocess.PIPE,
            shell=True, preexec_fn=os.setsid)  # 命令行启动appium服务

        # 如果没起来 就会进死循环 一直换端口 起appium服务
        while not util.check_appium_port_available(appium_port):
            util.wait_appium_port_available(appium_port)
            if util.check_appium_port_available(appium_port):
                break
            appium_port = util.create_port(server_ip, 4723, 7999)
            appium_p = subprocess.Popen(
                "appium -a {} -p {} --webdriveragent-port {} --relaxed-security "
                "--session-override --no-reset> {} 2>&1 &"
                .format(server_ip, appium_port, wda_port, appium_log_path), stdout=subprocess.PIPE,
                shell=True, preexec_fn=os.setsid)  # 命令行启动appium服务
    else:
        platform = GlobalVar.ANDROID
        GlobalVar.set_test_platform(platform)
        system_port = util.create_port(server_ip, 8200, 8299)
        if sys.platform.startswith("win"):
            appium_p = subprocess.Popen(
                "appium -a {} -p {} --relaxed-security --session-override --no-reset> {} 2>&1 &"
                .format(server_ip, appium_port, appium_log_path), shell=True)  # 命令行启动appium服务
        else:
            appium_p = subprocess.Popen(
                "appium -a {} -p {} --relaxed-security --session-override --no-reset> {} 2>&1 &"
                .format(server_ip, appium_port, appium_log_path), stdout=subprocess.PIPE, shell=True,
                preexec_fn=os.setsid)  # 命令行启动appium服务
        time.sleep(10)

    def kill_appium():
        try:
            if sys.platform.startswith("win"):
                p = os.popen("netstat -ano | findstr {}".format(appium_port))
                out = p.read().strip()
                begin = out.find("LISTENING") + len("LISTENING")
                end = out.find("\n", start=begin)
                pid = out[begin:end]
                os.popen("taskkill -PID {} -F".format(pid))
            else:
                os.killpg(os.getpgid(appium_p.pid + 1), signal.SIGTERM)  # 测试结束后，将appium进程杀掉
        except:
            pass
    # 注册kill_appium()为终结函数
    request.addfinalizer(kill_appium)


@pytest.fixture()
def driver_setup(request):
    """
    创建appium会话
    :param request:
    :return:
    """
    global driver, device_sn, device_name, platform_version, wda_port, platform
    if platform == GlobalVar.IOS:
        desired_capabilities = {
            "automationName": "XCUITest",
            "platformName": "ios",
            "deviceName": device_name,
            "bundleId": GlobalVar.get_bundle_id(),
            "udid": GlobalVar.get_device_sn(),
            "wdaLocalPort": wda_port,
            "newCommandTimeout": 3600,
            "clearSystemFiles": True,
            "wdaLaunchTimeout": 300000,
            "wdaConnectionTimeout": 300000,
            "noReset": True,
            "autoLaunch": False,
            "autoAcceptAlerts": False   # 自动关闭弹窗
        }
    else:
        desired_capabilities = {
            "automationName": "UiAutomator2",
            "platformName": "Android",
            "appPackage": GlobalVar.get_bundle_id(),
            "appActivity": GlobalVar.get_app_activity(),
            "udid": GlobalVar.get_device_sn(),
            "newCommandTimeout": 3600,
            "uiautomator2ServerInstallTimeout": 120000,
            "uiautomator2ServerLaunchTimeout": 120000,
            "systemPort": system_port,
            "orientation": "PORTRAIT",
            "noReset": True,
            "fullReset": False,
            "autoLaunch": False,
            "autoGrantPermissions": True
        }
    request.instance.driver = webdriver.Remote(command_executor='http://{}:{}/wd/hub'.format('127.0.0.1', appium_port),
                                               desired_capabilities=desired_capabilities)  # 创建会话
    request.instance.platform = platform
    driver = request.instance.driver
    if driver:
        logging.info(f"driver init finish...................")


def pytest_addoption(parser):
    """
    注册参数
    :param parser:
    :return:
    """
    parser.addoption("--device_sn", action="store", default="", help="手机设备号")
    parser.addoption("--bundle_id", action="store", default="com.android.settings", help="包名")
    parser.addoption("--app_activity", action="store", default="com.android.settings.Settings", help="启动activity")


def device_sn(request):
    """
    脚本获取命令行参数的接口：获取手机设备号
    :param request:
    :return:
    """
    value = request.config.getoption("--device_sn")
    return value


def bundle_id(request):
    """
    脚本获取命令行参数的接口：获取包名
    :param request:
    :return:
    """
    value = request.config.getoption("--bundle_id")
    return value


def app_activity(request):
    """
    脚本获取命令行参数的接口：获取启动activty
    :param request:
    :return:
    """
    value = request.config.getoption("--app_activity")
    return value